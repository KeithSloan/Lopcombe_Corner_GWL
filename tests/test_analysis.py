"""Tests for parsing readings into DataFrames and computing summary statistics."""

import unittest

import pandas as pd

from gwl import analysis

MEASURES = [
    {
        "@id": "http://environment.data.gov.uk/hydrology/id/measures/c962-gw-logged-i-subdaily-mAOD-qualified",
        "notation": "c962-gw-logged-i-subdaily-mAOD-qualified",
    },
    {
        "@id": "http://environment.data.gov.uk/hydrology/id/measures/c962-gw-dipped-i-mAOD-qualified",
        "notation": "c962-gw-dipped-i-mAOD-qualified",
    },
]


class ReadingsToDataFrameTests(unittest.TestCase):
    def test_sorts_by_datetime_and_parses_types(self):
        readings = [
            {"date": "2026-07-02", "dateTime": "2026-07-02T09:00:00", "value": 79.618, "quality": "Unchecked"},
            {"date": "2026-07-01", "dateTime": "2026-07-01T09:00:00", "value": 79.649, "quality": "Unchecked"},
        ]
        df = analysis.readings_to_dataframe(readings)
        self.assertEqual(list(df["value"]), [79.649, 79.618])
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["dateTime"]))

    def test_empty_input_returns_empty_frame_with_expected_columns(self):
        df = analysis.readings_to_dataframe([])
        self.assertEqual(list(df.columns), analysis.READING_COLUMNS)
        self.assertTrue(df.empty)


class ClassifyMeasuresTests(unittest.TestCase):
    def test_splits_logged_and_dipped_by_notation(self):
        split = analysis.classify_measures(MEASURES)
        self.assertEqual(len(split["logged"]), 1)
        self.assertEqual(len(split["dipped"]), 1)
        self.assertIn("logged", split["logged"][0]["notation"])
        self.assertIn("dipped", split["dipped"][0]["notation"])


class AnnualStatsTests(unittest.TestCase):
    def test_computes_max_and_percentile_per_year(self):
        df = analysis.readings_to_dataframe([
            {"date": "2024-01-01", "dateTime": "2024-01-01T09:00:00", "value": 10.0, "quality": "Good"},
            {"date": "2024-06-01", "dateTime": "2024-06-01T09:00:00", "value": 20.0, "quality": "Good"},
            {"date": "2025-01-01", "dateTime": "2025-01-01T09:00:00", "value": 5.0, "quality": "Good"},
        ])
        stats = analysis.annual_stats(df, percentile=90)
        row_2024 = stats[stats["year"] == 2024].iloc[0]
        row_2025 = stats[stats["year"] == 2025].iloc[0]
        self.assertEqual(row_2024["max"], 20.0)
        self.assertEqual(row_2025["max"], 5.0)
        self.assertEqual(row_2024["count"], 2)

    def test_works_after_concat_with_an_empty_series(self):
        # Regression: a dipped-only station has no logged series at all, so
        # run.py concatenates real dipped readings with an empty logged
        # frame. If the empty frame's dateTime column isn't datetime64,
        # concat silently downgrades the combined column to `object` and
        # `.dt.year` blows up.
        dipped_df = analysis.readings_to_dataframe([
            {"date": "2024-03-01", "dateTime": "2024-03-01T09:00:00", "value": 15.0, "quality": "Good"},
        ])
        empty_logged_df = analysis.fetch_series(client=None, measures=[])
        combined = pd.concat([dipped_df, empty_logged_df], ignore_index=True)
        stats = analysis.annual_stats(combined, percentile=90)
        self.assertEqual(stats[stats["year"] == 2024].iloc[0]["max"], 15.0)


class LastNDaysTests(unittest.TestCase):
    def test_filters_to_trailing_window(self):
        df = analysis.readings_to_dataframe([
            {"date": "2026-07-01", "dateTime": "2026-07-01T09:00:00", "value": 1.0, "quality": "Good"},
            {"date": "2026-07-10", "dateTime": "2026-07-10T09:00:00", "value": 2.0, "quality": "Good"},
            {"date": "2026-07-17", "dateTime": "2026-07-17T09:00:00", "value": 3.0, "quality": "Good"},
        ])
        trimmed = analysis.last_n_days(df, days=7, reference="2026-07-17")
        self.assertEqual(list(trimmed["value"]), [2.0, 3.0])


class DetectDiscrepantReadingsTests(unittest.TestCase):
    def setUp(self):
        # Logged/telemetry reference series: a steady ~82-83 mAOD through the period.
        self.reference_df = analysis.readings_to_dataframe([
            {"date": "2025-05-14", "dateTime": "2025-05-14T09:00:00", "value": 82.90, "quality": "Good"},
            {"date": "2025-05-15", "dateTime": "2025-05-15T09:00:00", "value": 82.71, "quality": "Missing"},
            {"date": "2025-05-16", "dateTime": "2025-05-16T09:00:00", "value": 82.60, "quality": "Good"},
        ])

    def test_flags_reading_far_from_reference(self):
        dipped = analysis.readings_to_dataframe([
            {"date": "2025-05-15", "dateTime": "2025-05-15T10:00:00", "value": 105.08, "quality": "Good"},
        ])
        clean, discrepant = analysis.detect_discrepant_readings(dipped, self.reference_df, max_diff=5.0)
        self.assertTrue(clean.empty)
        self.assertEqual(len(discrepant), 1)
        self.assertAlmostEqual(discrepant.iloc[0]["reference_value"], 82.71)
        self.assertAlmostEqual(discrepant.iloc[0]["diff"], 105.08 - 82.71, places=3)

    def test_keeps_reading_close_to_reference(self):
        dipped = analysis.readings_to_dataframe([
            {"date": "2025-05-15", "dateTime": "2025-05-15T10:00:00", "value": 82.75, "quality": "Good"},
        ])
        clean, discrepant = analysis.detect_discrepant_readings(dipped, self.reference_df, max_diff=5.0)
        self.assertEqual(len(clean), 1)
        self.assertTrue(discrepant.empty)

    def test_keeps_reading_with_no_reference_in_tolerance(self):
        # Pre-dates the reference series by far more than the tolerance window - can't be checked.
        dipped = analysis.readings_to_dataframe([
            {"date": "1963-04-23", "dateTime": "1963-04-23T12:00:00", "value": 83.36, "quality": "Good"},
        ])
        clean, discrepant = analysis.detect_discrepant_readings(
            dipped, self.reference_df, max_diff=5.0, tolerance_hours=24,
        )
        self.assertEqual(len(clean), 1)
        self.assertTrue(discrepant.empty)

    def test_empty_inputs_return_unfiltered_copy(self):
        dipped = analysis.readings_to_dataframe([
            {"date": "2025-05-15", "dateTime": "2025-05-15T10:00:00", "value": 82.75, "quality": "Good"},
        ])
        empty_reference = analysis.readings_to_dataframe([])
        clean, discrepant = analysis.detect_discrepant_readings(dipped, empty_reference, max_diff=5.0)
        self.assertEqual(len(clean), 1)
        self.assertTrue(discrepant.empty)


if __name__ == "__main__":
    unittest.main()

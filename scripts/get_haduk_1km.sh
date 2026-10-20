#!/bin/bash
# Download HadUK-Grid 1 km monthly rainfall, 1963-2025, to the Crucial SSD.
# Usage: bash get_haduk_1km.sh   (asks for CEDA username + password, gets a token)
set -u
DEST="/Volumes/Crucial X9 Pro for Mac/HadUK-Grid"
VER="v1.3.2.ceda"
REL="v20260512"
URL="https://dap.ceda.ac.uk/badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/$VER/1km/rainfall/mon/$REL"
TOKEN_API="https://services.ceda.ac.uk/api/token/create/"

# --- Get a fresh access token from the CEDA Token API ---
read -rp "CEDA username: " CEDA_USER
read -rsp "CEDA password: " CEDA_PASS; echo
resp=$(curl -s -X POST "$TOKEN_API" \
  -H "Authorization: Basic $(printf '%s' "$CEDA_USER:$CEDA_PASS" | base64)")
unset CEDA_PASS
CEDA_TOKEN=$(printf '%s' "$resp" | python3 -c \
  'import sys,json
try: print(json.load(sys.stdin)["access_token"])
except Exception: pass')
if [ -z "$CEDA_TOKEN" ]; then
  echo "Token request failed. CEDA replied:"
  printf '%s\n' "$resp" | head -c 600; echo
  exit 1
fi
echo "Got token (length ${#CEDA_TOKEN})"

mkdir -p "$DEST" || { echo "Can't create $DEST - is the drive mounted?"; exit 1; }
echo "Saving to: $DEST"
echo "Source:    $URL"

missing=()
for y in $(seq 1963 2025); do
  f="rainfall_hadukgrid_uk_1km_mon_${y}01-${y}12.nc"
  out="$DEST/$f"
  if [ -s "$out" ]; then echo "have  $f"; continue; fi
  echo "fetch $f"
  curl -fL --retry 3 -C - -H "Authorization: Bearer $CEDA_TOKEN" \
       -o "$out.part" "$URL/$f"
  rc=$?
  if [ $rc -eq 22 ]; then          # HTTP error, e.g. 404: year not published
    rm -f "$out.part"; missing+=("$y"); continue
  elif [ $rc -ne 0 ]; then
    rm -f "$out.part"
    echo "curl failed with code $rc on $f - stopping. Paste this output to Claude."
    exit 1
  fi
  # Real NetCDF starts with "CDF" (classic) or "\x89HDF" (NetCDF-4)
  magic=$(head -c 4 "$out.part" | LC_ALL=C tr -dc 'A-Za-z')
  if [ "$magic" != "CDF" ] && [ "$magic" != "HDF" ]; then
    echo
    echo "ERROR: $f is not a NetCDF file ($(wc -c < "$out.part") bytes). Server sent:"
    head -c 600 "$out.part"; echo
    rm -f "$out.part"
    echo "Stopping - paste this output to Claude (it contains no token)."
    exit 1
  fi
  mv "$out.part" "$out"
done
echo "Done. Not available: ${missing[*]:-none}"

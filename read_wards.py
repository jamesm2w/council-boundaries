import json
import csv

ward_authority_lookup = {}
authority_lookup = {}

new_ward_data = []

council_wards = {}

with open("WD21_LAD21_UK_LU.csv", "r") as lookup_file:
    print("Opening Ward->LAD lookup file");

    reader = csv.reader(lookup_file, delimiter=",")
    linec = 1
    max_linec = 8695 # Number of lines in the file -- Should be the same as the number of wards
    for line in reader:
        print("Processing line: ", linec, "/", max_linec, end="\r")
        [wd21cd, wd21nm, lad21cd, lad21nm] = line
        ward_authority_lookup[wd21cd] = (wd21cd, wd21nm, lad21cd, lad21nm)
        authority_lookup[lad21cd] = lad21nm
        council_wards[lad21cd] = []
        linec += 1

    print("\nFinished Processing Ward->LAD lookups")
    print("Lookup Length: ", len(ward_authority_lookup.keys()))

with open("Wards_(December_2021)_GB_BFC.geojson", "r") as wards_file:
    print("Opening Wards GeoJSON file")
    ward_data = json.load(wards_file)
    print("Wards GeoJSON file loaded")

    wardc = 1
    max_wardc = len(ward_data["features"])
    for ward in ward_data["features"]:
        print("Processing Ward: ", wardc, "/", max_wardc, end="\r")
        
        if ward["properties"]["WD21NM"] != ward_authority_lookup[ward["properties"]["WD21CD"]][1]:
            print("\n", wardc, ": false on name check Boundary:", ward["properties"]["WD21NM"], " Lookup:", ward_authority_lookup[ward["properties"]["WD21CD"]][1], end="\n")
        
        new_ward_obj = {
            "type": "Feature",
            "properties": {
                "id": ward["properties"]["OBJECTID"],
                "wdnm":  ward["properties"]["WD21NM"],
                "wdnmw": ward["properties"]["WD21NMW"],
                "wdcd":  ward_authority_lookup[ward["properties"]["WD21CD"]][0],
                "ladcd": ward_authority_lookup[ward["properties"]["WD21CD"]][2],
                "ladnm": ward_authority_lookup[ward["properties"]["WD21CD"]][3],
                "lnglat": [ward["properties"]["LONG"], ward["properties"]["LAT"]]
            },
            "geometry": ward["geometry"]
        }

        new_ward_data.append(new_ward_obj)
        council_wards[ward_authority_lookup[ward["properties"]["WD21CD"]][2]].append(new_ward_obj)
        wardc += 1

    print("\nFinished Processing Wards                                                  ")
    print("Wards Length: ", len(new_ward_data))


with open("output/wards_gb.geojson", "w") as output_file:
    print("Writing output file")
    output_obj = {
        "type": "FeatureCollection",
        "name": "GB_Wards_21",
        "properties": {
            "generatedby": "read_wards.py",
            "crs": "urn:ogc:def:crs:OGC:1.3:CRS84"
        },
        "features": new_ward_data
    }
    json.dump(output_obj, output_file)
    print("Finished Writing output file")

councilc = 1
max_councilc = len(council_wards.keys())
for councilKey in council_wards:
    name = authority_lookup[councilKey]
    with open("output/wards_" + name.replace(".", "").replace(",", "").replace(" ", "_") + ".geojson", "w") as output_file:
        print("Writing output file", councilc, "/", max_councilc, "for Council:", name, end="                         \r")
        output_obj = {
            "type": "FeatureCollection",
            "name": "GB_Wards_21_"+name.replace(" ", "_"),
            "properties": {
                "generatedby": "read_wards.py",
                "crs": "urn:ogc:def:crs:OGC:1.3:CRS84"
            },
            "features": council_wards[councilKey]
        }
        json.dump(output_obj, output_file)
        # print("Finished Writing output file for Council: ", councilKey)
        councilc += 1

with open("output/council_index.json", "w") as output_file:
    index_obj = { c: {
        "code": c,
        "name": authority_lookup[c], 
        "file": "wards_" + authority_lookup[c].replace(".", "").replace(",", "").replace(" ", "_") + ".geojson"
    } for c in council_wards.keys() }

    json.dump(index_obj, output_file)

print("\nFinished")
a = input()
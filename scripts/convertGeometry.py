import requests
import json
import sys

if not len(sys.argv) == 2:
    print("Wrong number of arguments: python3 convertGeometry.py /path/to/plz.csv")

lks = json.loads(requests.get("http://172.16.0.162:8800/data/geo/lk?geometry=true").text)
my_lks = {}
for lk in lks:
    my_lks[lk["id"]] = {"name":lk["name"],"geo":lk["geometry"],"plz":[],"cities":[]}

def searchloop(name, noParenthesis = False):
    for key, value in my_lks.items():
        district = value["name"]
        search = name
        if district.endswith(" (Kreis)"):
            district = district.replace(" (Kreis)", "")
        if district.endswith(" (Stadt)"):
            district = district.replace(" (Stadt)", "")
        if search.startswith("Landkreis "):
            search = search.replace("Landkreis ", "")
        if search.startswith("Kreis "):
            search = search.replace("Kreis ", "")
        if noParenthesis and " (" in district and district.endswith(")"):
            districtParts = district.split(" ")
            district = ""
            first = True
            for i in range(len(districtParts) - 1):
                if not first:
                    district = district + " "
                else:
                    first = False
                district = districtParts[i]
        if district == search:
            return key
    return -1

def getIdForName(name):
    pass1 = searchloop(name)
    if pass1 >= 0:
        return pass1
    newName = name.replace(" an der ", " a.d. ").replace(" im ", " i. ").replace(" am ", " a. ").replace(" in der ", " i.d. ").replace("Oberpfalz", "OPf.").replace(" - Chóśebuz", "")
    pass2 = searchloop(newName)
    if pass2 >= 0:
        return pass2
    pass3 = searchloop(newName, True)
    if pass3 >= 0:
        return pass3
    if "/" in newName:
        replaceSlash = newName.split("/")
        search = ""
        first = True
        for i in range(len(replaceSlash) - 1):
            if not first:
                search = search + " "
            else:
                first = False
            search = replaceSlash[i]
        search = search + " (" + replaceSlash[-1] + ")"
        pass4 = searchloop(search)
        if pass4 >= 0:
            return pass4
    return -1

fails = 0
succs = 0

berlin = {
    "Berlin Mitte": ["10115", "10117", "10119", "10178", "10179", "10435", "10551", "10553", "10555", "10557", "10559", "10623", "10785", "10787", "10963", "10969", "13347", "13349", "13351", "13353", "13355", "13357", "13359", "13405", "13407", "13409"],
    "Berlin Friedrichshain-Kreuzberg": ["10179", "10243", "10245", "10247", "10249", "10367", "10785", "10961", "10963", "10965", "10967", "10969", "10997", "10999", "12045", "10178"],
    "Berlin Pankow": ["10119", "10247", "10249", "10405", "10407", "10409", "10435", "10437", "10439", "13051", "13053", "13086", "13088", "13089", "13125", "13127", "13129", "13156", "13158", "13159", "13187", "13189"],
    "Berlin Charlottenburg-Wilmersdorf": ["10553", "10585", "10587", "10589", "10623", "10625", "10627", "10629", "10707", "10709", "10711", "10713", "10715", "10717", "10719", "10777", "10779", "10787", "10789", "10825", "13353", "13597", "13627", "13629", "14050", "14052", "14053", "14055", "14057", "14059", "14193", "14195", "14197", "14199"],
    "Berlin Spandau": ["13581", "13583", "13585", "13587", "13589", "13591", "13593", "13595", "13597", "13599", "13627", "13629", "14052", "14089"],
    "Berlin Steglitz-Zehlendorf": ["12157", "12161", "12163", "12165", "12167", "12169", "12203", "12205", "12207", "12209", "12247", "12249", "12277", "12279", "14109", "14129", "14163", "14165", "14167", "14169", "14193", "14195", "14197", "14199"],
    "Berlin Tempelhof-Schöneberg": ["10777", "10779", "10781", "10783", "10785", "10787", "10789", "10823", "10825", "10827", "10829", "10965", "12099", "12101", "12103", "12105", "12107", "12109", "12157", "12159", "12161", "12163", "12169", "12249", "12277", "12279", "12305", "12307", "12309", "12347", "14197"],
    "Berlin Neukölln": ["10965", "10967", "12043", "12045", "12047", "12049", "12051", "12053", "12055", "12057", "12059", "12099", "12107", "12305", "12347", "12349", "12351", "12353", "12355", "12357", "12359"],
    "Berlin Treptow-Köpenick": ["12435", "12437", "12439", "12459", "12487", "12489", "12524", "12526", "12527", "12555", "12557", "12559", "12587", "12589", "12623"],
    "Berlin Marzahn-Hellersdorf": ["12555", "12619", "12621", "12623", "12627", "12629", "12679", "12681", "12683", "12685", "12687", "12689"],
    "Berlin Lichtenberg": ["10315", "10317", "10318", "10319", "10365", "10367", "10369", "13051", "13053", "13055", "13057", "13059"],
    "Berlin Reinickendorf": ["13403", "13405", "13407", "13409", "13435", "13437", "13439", "13465", "13467", "13469", "13503", "13505", "13507", "13509", "13599", "13629"]
}

for key, value in berlin.items():
    id = getIdForName(key)
    for v in value:
        my_lks[id]["plz"].append(v)
        succs += 1

with open(sys.argv[1], "r") as f:
    first = True
    for line in f.readlines():
        if first:
            first = False
            continue
        elif "Berlin" in line:
            continue
        else:
            lineData = line.split(",")
            searchFor = lineData[4].strip()
            if searchFor == "":
                searchFor = lineData[2].strip()
            lkId = getIdForName(searchFor)
            if lkId < 0:
                print("Unable to find id for " + lineData[4] + "(" + lineData[2] + ")");
                fails += 1
            else:
                if not lineData[3].strip() in my_lks[lkId]["plz"]:
                    my_lks[lkId]["plz"].append(lineData[3].strip())
                if not lineData[2].strip() in my_lks[lkId]["cities"] and not lineData[2].strip() == my_lks[lkId]["name"]:
                    my_lks[lkId]["cities"].append(lineData[2].strip())
                succs += 1

with open("geo.json", "w") as f:
    f.write(json.dumps(my_lks))

print("Found " + str(succs))
print("Failed for " + str(fails))

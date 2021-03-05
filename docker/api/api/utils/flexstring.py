#!/usr/bin/env python3

# Corona-Info-App
# flexstring-Parser
# © 2020 Tobias Höpp.

#######################################
# DOCUMENTATION: flexstring (Funktion: flexstringParse(flexstring,configuration))
# Die funktion dient dem auswerten von flexstrings, also strings, die selbst variablen beinhalten, die konfiguriert werden können.
# Das ermöglicht z.B. das einfache Anpassen von Daten in sehr vielen Sprachen.
# Steuerzeichen: $, [ , ] {, }, \
#   müssen mit einem \ escaped werden, wenn sie im text vorkommen sollen. Außnahme: \n benötigt kein escaping als einzig zulässiges steuerzeichen.
# Mögliche Variablen-Typen: Boolean, String, Int, Array, Enum
# NAME stellt im folgenden den Variablennamen dar. Dieser ist case-sensitiv (Groß-kleinschreibung) und muss mit gültigem Wert in der Konfiguration vorhanden sein.
# Der Variablenname darf KEINE Unterstriche enthalten.
# Boolean:
#   Booleans werden durch 
#      $_NAME_{TEXT}{KONJUNKTION} oder $_NAME_{TEXT}
#   dargestellt.
#      $!_NAME_{TEXT}{KONJUNKTION} oder $!_NAME_{TEXT}
#   negiert den Wert des booleans.
#   TEXT, KONJUNKTION, sind hierbei wieder ein flexstring (können also selbst Variablen enthalten). 
#   TEXT oder KONJUNKTION wird angezeigt, wenn der Boolean den Wert True hat. (bzw. ggf. seine negation)
#   Werden mehrere Booleans direkt hintereinander (ohne Zeichen dazwischen) aufgelistet, so handelt es sich um eine BooleanList.
#   Eine BooleanList endet automatisch, wenn ein Boolean keine KONJUNCTION beinhaltet oder auf einen Boolean etas anderes als direkt ein Boolean folgt. 
#   Ist ein weiterer Boolean in der BooleanList True, so wird KONJUNKTION anstelle von TEXT angezeigt
#   Der Wert der Variable NAME muss ein Boolean (Wahrheitswert), also True ^= 1 oder False ^= 0 sein.  
# String, Int:
#   Strings und Integer werden durch
#       $_NAME_
#   ohne (direkt) folgende Klammer dargestellt.
#   Sie werden 1:1 abgedruckt.
#   Hinweis: Die Variable eines Integers kann (theoretisch) gleichzeitig als enum verwendet werden. Davon ist jedoch abzuraten.
#   Der Wert der Variable NAME muss ein Integer (Zahl) oder String (Text) sein.  
# Array:
#   Arrays werden durch
#       $_NAME_[[{ANFANG}{ENDE-BEI-KONJUNKTION}{ENDE-LETZTES}]]
#   dargestellt.
#   ANFANG, ENDE-BEI-KONJUNKTION, ENDE-LETZTES sind dabei wieder flexstring (können also Variablen beinhalten).
#   ANFANG wird vor jedem Element des Arrays, das vom Typ String sein muss, angezeigt.
#   darauf folgt der eigentliche string
#   ENDE-BEI-KONJUNKTION wird nach jedem Element des Arrays angezeigt, außer dem letzten Element. Dort wird ENDE-LETZTES verwendet.
#   Der Wert der Variable NAME muss ein Array (Liste) von Strings sein.  
# Enum:
#   Enums werden durch
#        $_NAME_[{ELEMENT0},{ELEMENT1},{ELEMENT2}]
#   dargestellt.
#   ELEMENT0, ELEMENT1 usw. sond dabei wieder flexstring (können also Variablen beinhalten).
#   Auf das letzte Element darf kein Komma folgen. Sonst sind alle Elemente durch exakt ein Komma voneinander getrennt und von geschweiften Klammern umgeben.
#   Der Wert der Variable NAME muss ein nicht-negativer Integer (oder Boolean: True = 1, False = 0) sein. 
#   Das Element, welches an der Position mit der Nummer des Integerwertes steht, wird angezeigt. Das erste Element hat die Nummer 0.
#######################################

def flexstringParse(s, conf):
    try:
        result = ""
        pos = 0
        conjunction = ""
        noconjunction = ""
        while pos < len(s):
            if s[pos] == "$":
                #Variable
                #First check if negated
                if s[pos+1] == "!":
                    pos += 1
                    negate = True
                else:
                    negate = False
                # Name der Variable ermitteln
                if not s[pos+1] == "_":
                    return 0, "Syntax error: _ missing at position ", pos+1
                pos +=2
                p = pos
                c = False
                while p < len(s):
                    if s[p] == "_":
                        c = True
                        break
                    elif s[p] in ["\\", "[", "]", "{", "}", "$"]:
                        return 0, "Syntax error: unexpectet character '"+s[p]+"' in variable name at position", pos
                    p +=1
                if not c:
                    return 0, "Syntax error: missing _ for end of variablename for variable", pos-1
                if p == pos:
                    return 0, "Syntax error: missing variable name", pos-1
                varName = s[pos:p]
                if varName not in conf:
                    return 0, "Configuration Error: variable '"+varName+"' not found", pos
                #Typ der Variable ermitteln:
                pos = p+1
                if pos < len(s)-1 and s[pos] == "{":
                    #Ist boolean
                    # get arguments
                    p1 = closingPosition(s[pos+1:],"{","}")
                    if p1 == 0:
                        return 0, "Syntax Error: could not find closing bracket for opening bracket", pos
                    p1 += pos+1
                    noconj = s[pos+1:p1]
                    #conjunction
                    if p1+1 < len(s) and s[p1+1] == "{":
                        p2 = closingPosition(s[p1+2:],"{","}")
                        if p2 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", p1+1
                        p2+=p1+2
                        conj = s[p1+2:p2]
                        p3 = p2
                    else:
                        conj = noconj
                        p3 = p1
                    #evaluate value:
                    if not (isinstance(conf[varName],bool) or (isinstance(conf[varName],int) and (conf[varName] ==1 or conf[varName] ==0))):
                        return 0, "Configuration Error: variable '"+varName+"' is supposed to be bool, but has value '"+str(conf[varName])+"'", 0
                    boolval = negate != conf[varName]
                    if boolval:
                        if conjunction != "":
                            # Füge vorangegangenen Boolean als ein
                            ok, res, ep = flexstringParse(conjunction, conf)
                            if not ok:
                                return 0, "Syntax Error while parsing boolStatement '"+conjunction+"': "+res+" at position "+str(ep)+".", pos
                            result += res
                        conjunction = conj
                        noconjunction = noconj
                            # noconjunction wird angezeigt, wenn auf den Boolean kein weiterer folgt. Sonnst wird conjunction angezeigt.
                    pos = p3
                elif pos < len(s)-1 and s[pos] == "[":
                    # Vorangegangene Booleanliste beenden
                    conjunction = ""
                    if noconjunction != "":
                        # Füge vorangegangenen Boolean ein
                        ok, res, ep = flexstringParse(noconjunction, conf)
                        if not ok:
                            return 0, "Syntax Error while parsing boolStatement '"+noconjunction+"': "+res+" at position "+str(ep)+".", pos
                        result += res 
                        noconjunction = ""
                    # Eigentliche Auswertung
                    if s[pos+1] == "[":
                        #Ist array
                        p1 = closingPosition(s[pos+2:],"[[","]]")
                        if p1 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", pos
                        p1 += pos+2 #position of first closing bracket

                        #Extract Arguments required to pass array:
                        #First
                        if s[pos+2] != "{":
                            return 0, "Syntax Error: could not find first argument to parse array", pos+1
                        p2 = closingPosition(s[pos+3:p1],"{","}")
                        if p2 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", pos+2
                        p2 += pos+3
                        ok, res, ep = flexstringParse(s[pos+3:p2],conf)
                        if not ok:
                            print(s[pos+4:p2])
                            return 0, res, ep+pos+4
                        arrBegin = res
                        #Second
                        if s[p2+1] != "{":
                            return 0, "Syntax Error: could not find second argument to parse array", p2+1
                        p3 = closingPosition(s[p2+2:p1],"{","}")
                        if p3 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", p2+1
                        p3 += p2+2
                        ok, res, ep = flexstringParse(s[p2+2:p3],conf)
                        if not ok:
                            return 0, res, ep+p2+2
                        arrCon = res
                        #Third
                        if s[p3+1] != "{":
                            return 0, "Syntax Error: could not find third argument to parse array", p3+1
                        p4 = closingPosition(s[p3+2:p1],"{","}")
                        if p4 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", p3+1
                        p4 += p3+2
                        ok, res, ep = flexstringParse(s[p3+2:p4],conf)
                        if not ok:
                            return 0, res, ep+p3+2
                        arrEnd = res
                        #check if that was all for the array:
                        if p4+1!=p1:
                            return 0, "Syntax Error: array does not end with third argument", p4+1
                        
                        #Iterate over array
                        if not isinstance(conf[varName], list):
                            return 0, "Type Error: Variable '"+varName+"' is not an array.", pos
                        for i, v in enumerate(conf[varName]):
                            if not isinstance(v,str):
                                return 0, "Type Error: Array '"+varName+"' does not only contain strings", pos #TODO: Use exeption instead
                            result+=arrBegin
                            result+=v #TODO: IMPORTANT: escape string content of v
                            if i < len(conf[varName])-1:
                                result+=arrCon
                            else:
                                result+=arrEnd
                        #Set new position
                        pos = p1+1
                    else:
                        #Ist enum
                        p1 = closingPosition(s[pos+1:],"[","]")
                        if p1 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", pos
                        p1 += pos+1
                        if not (isinstance(conf[varName], int)):
                            return 0, "Type Error: Variable '"+varName+"' is not an int.", pos-1
                        p3 = pos
                        if conf[varName] < 0:
                            return 0, "Type Error: Variable '"+varName+"'is negativ.", pos-1
                        for i in range(conf[varName]+1):
                            p2 = p3 +1
                            if s[p2] == "]":
                                return 0, "Value Error: enum variable '"+varName+"' out of range with id '"+str(conf[varName])+"'", p2
                            if i != 0:
                                if s[p2] != ",":
                                    return 0, "Syntax Error: expected ',' separating enum values. Found '"+s[p2]+"' instead.", p2
                                p2 +=1
                            if s[p2] != "{":
                                return 0, "Syntax Error: unexpectet character '"+s[p2]+"' in enum", p2
                            p3 = closingPosition(s[p2+1:p1],"{","}")
                            if p3 == 0:
                                return 0, "Syntax Error: could not find closing bracket for opening bracket", p2
                            p3 += p2+1
                        ok, res, ep = flexstringParse(s[p2+1:p3],conf)
                        if not ok:
                            return 0, res, ep+pos+4
                        result+=res
                        pos = p1+1
                else:
                    # Vorangegangene Booleanliste beenden
                    conjunction = ""
                    if noconjunction != "":
                        # Füge vorangegangenen Boolean ein
                        ok, res, ep = flexstringParse(noconjunction, conf)
                        if not ok:
                            return 0, "Syntax Error while parsing boolStatement '"+noconjunction+"': "+res+" at position "+str(ep)+".", pos
                        result += res 
                        noconjunction = ""
                    # Eigentliche Auswertung
                    if not (isinstance(conf[varName], int) or isinstance(conf[varName], str)):
                        return 0, "Type Error: Variable '"+varName+"' is not a string or int.", pos-1
                    if isinstance(conf[varName],int) or isinstance(conf[varName],float):
                        result += str(abs(conf[varName]))
                    else:
                        result += str(conf[varName])#TODO: IMPORTANT: escape string content of v
                    pos -= 1 #make pos point to the right position
            elif s[pos] == "\\":
                # Vorangegangene Booleanliste beenden
                conjunction = ""
                if noconjunction != "":
                    # Füge vorangegangenen Boolean ein
                    ok, res, ep = flexstringParse(noconjunction, conf)
                    if not ok:
                        return 0, "Syntax Error while parsing boolStatement '"+noconjunction+"': "+res+" at position "+str(ep)+".", pos
                    result += res 
                    noconjunction = ""
                # Eigentliche Auswertung
                #skip escaped arguments
                pos += 1
                if s[pos] == "n":
                    # pass line endings
                    result += "\\"
                result += s[pos]
            elif s[pos] in ["{","}","[","]"]:
                return 0, "unexpected character '"+s[pos]+"'. (If you want to actually have it displayed, try using a \\ (Backslash) in front of it.", pos
            else:
                # Vorangegangene Booleanliste beenden
                conjunction = ""
                if noconjunction != "":
                    # Füge vorangegangenen Boolean ein
                    ok, res, ep = flexstringParse(noconjunction, conf)
                    if not ok:
                        return 0, "Syntax Error while parsing boolStatement '"+noconjunction+"': "+res+" at position "+str(ep)+".", pos
                    result += res 
                    noconjunction = ""
                # Eigentliche Auswertung
                result += s[pos]
            pos +=1
        # Vorangegangene Booleanliste beenden
        conjunction = ""
        if noconjunction != "":
            # Füge vorangegangenen Boolean ein
            ok, res, ep = flexstringParse(noconjunction, conf)
            if not ok:
                return 0, "Syntax Error while parsing boolStatement '"+noconjunction+"': "+res+" at position "+str(ep)+".", pos
            result += res 
            noconjunction = ""
        # Eigentliche Auswertung
        return 1, result, None
    except IndexError:
        return 0, "Unexpected end of (sub)-string", len(s)
        #TODO: das mal ordentlich machen

def closingPosition(s,opening,closing):
    #INPUT:
    # s: String starting right after opening bracket
    # opening: opening bracket
    # closing: closing bracket
    if len(opening) != len(closing):
        Exception("length of opening bracket '"+opening+"' does not match lenth of closing bracket '"+closing+"'")
    l = len(closing)
    p = 0
    c = 1
    while p < len(s)-l+1:
        if s[p:p+l] == opening:
            c +=1
        elif s[p:p+l] == closing:
            c -=1
        elif s[p] == '\\':
            # skip escaped character
            p += 1
            if len(s)-l+1 < p:
                # Handle index range error
                return 0
        if c == 0: 
            break #p is now the position of the closing bracket
        p +=1
    # Break in case of syntax error:
    if c != 0:
        return 0
    return p #Anfangsposition der schließenden Klammer

################################
# Function for variables list
class variableList():
    variableList = dict
    # Constructor
    def __init__(self):
        self.variableList = {}
    def append(self, name, vartype, maxval=None):
        if name not in self.variableList:
            if vartype == "int":
                self.variableList[name] = {"type":"int","max":maxval}
            else:
                self.variableList[name] = {"type":vartype}
        elif self.variableList[name]["type"] != vartype:
            if (self.variableList[name]["type"]  == "bool" and vartype in ("str", "int")) or (self.variableList[name]["type"]  == "int" and vartype == "str"):
                return True
            elif self.variableList[name]["type"]  == "int" and vartype == "bool":
                self.variableList[name] = {"type":"bool"}
            elif self.variableList[name]["type"]  == "str" and vartype == "bool":
                self.variableList[name]["type"]  = "bool"
            elif self.variableList[name]["type"]  == "str" and vartype == "int":
                self.variableList[name] = {"type":"int","max":maxval}
            return False
        return True
# Validation of varlists
def validateVarList(subset, varlist):
    for name in subset:
        if name not in varlist:
            return 0, "variable '"+name+"' is not defined"
        if subset[name]["type"] == "bool":
            if varlist[name]["type"] != "bool": #and not (varlist[name]["type"] == "int" and varlist[name]["max"] == 1):
                return 0, "variable '"+name+"' is required to be of type '"+varlist[name]["type"]+"' but has type 'bool'"
        elif subset[name]["type"] == "int":
            #if varlist[name]["type"] == "bool":
            #    if not subset[name]["max"] != 1:
            #        return 0, "variable '"+name+"' can only have a maxvalue of 1"
            if varlist[name]["type"] == "int":
                #if varlist[name]["max"] < subset[name]["max"]:
                #    return 0, "variable '"+name+"' can only have a maxvalue of "+str(varlist[name]["max"])
                # Do not check if the list is to long, as this will not cause any errors but might be unintentional
                if not isinstance(varlist[name]["max"],int):
                    return 0, "JSON Syntax Error: '"+name+"'['max'] has to be a number, but is not."
                if varlist[name]["max"] > subset[name]["max"]:
                    return 0, "variable '"+name+"' has to allow for values as high as "+str(varlist[name]["max"])+", but only allows for values as high as "+str(subset[name]["max"])
            elif varlist[name]["type"] != "bool":
                return 0, "variable '"+name+"' is required to be of type '"+varlist[name]["type"]+"' but has type 'int'"
        elif subset[name]["type"] == "arr":
            if varlist[name]["type"] != "arr":
                return 0, "variable '"+name+"' is required to be of type '"+varlist[name]["type"]+"' but has type 'arr'"
        elif subset[name]["type"] == "str":
            if varlist[name]["type"] == "arr":
                return 0, "variable '"+name+"' is required to be of type 'arr' but has type 'str'"
    return 1, None
# Validation of configurations
def validateConfig(config,varlist):
    if varlist == None:
        return 1, None
    for name in varlist:
        if name not in config:
            return 0, "variable '"+name+"' is required but not in configuration"
        if varlist[name]["type"] == "bool" and not(isinstance(config[name], bool)):# or (isinstance(config[name], int) and 0<=config[name]<=1)):
            return 0, "variable '"+name+"' is required to be bool"
        elif varlist[name]["type"] == "int":
            if not(isinstance(config[name], int)):
                return 0, "variable '"+name+"' is required to be int"
            if "max" in varlist[name]:
                if config[name] > varlist[name]["max"] or config[name]<0:
                    return 0, "variable '"+name+"' must be int between 0 and "+str(varlist[name]["max"])
        elif varlist[name]["type"] == "arr":
            if not(isinstance(config[name], list)):
                return 0, "variable '"+name+"' is required to be array"
            for li in config[name]:
                if not(isinstance(li, str)):
                    return 0, "array '"+name+"' must only contain strings"
        elif varlist[name]["type"] == "float":
            if not(isinstance(config[name], float)) and not(isinstance(config[name], int)):
                return 0, "variable '"+name+"' is required to be float or int"
        elif varlist[name]["type"] == "str":
            if not(isinstance(config[name], str) or isinstance(config[name], int) or isinstance(config[name], float)):
                return 0, "variable '"+name+"' is required to be string"
    return 1, None

# check if varlist is mergable
def isMergable(varlist):
    for name in varlist:
        if varlist[name]["type"] == "str":
            return False
        elif varlist[name]["type"] == "int" and "maxval" in varlist[name]:
            return False
    return True

def mergeConfig(conf1, conf2):
    if conf1.keys() != conf2.keys():
        return False
    conf = {}
    for name in conf1:
        if type(conf1[name]) != type(conf2[name]):
            return False
        if isinstance(conf1[name], bool):
            conf[name] = conf1[name] or conf2[name]
            # booleans werden verordert
        elif isinstance(conf1[name], int) or isinstance(conf1[name], float):
            if conf1[name] < conf2[name]:
                conf[name] = conf1[name]
            else:
                conf[name] = conf2[name]
            # bei integern/floats wird der kleinste Wert genommen. Soll der größte Wert genommen werden, negative Zahlen verwenden. Diese werden als Betrag angezeigt. #TODO
        elif isinstance(conf1[name], list):
            tmp = conf2[name].copy()
            conf[name] = []
            for li in conf1[name]:
                conf[name].append(li)
                if li in tmp:
                    tmp.remove(li)
                    # remove duplicats
            for li in tmp:
                conf[name].append(li)
            # TODO: Alphabetically order?
        else:
            return False
    return conf

################################################
# MODIFICATIONS FOR SYNTAX-CHECK:
# GENERAL changes: use flexstringSyntax instead of flexstringParse and remove everything that has "conf" in it
# For BOOLEAN: Add conj and nocony straight away and remove everything with conjunction and noconjunction
# For ENUM iteration
#   while true instead of range and break if s[p2] == "]"
#       define i as 0 and make it increment
#   Add ok, res, ep = flexstringSyntax(s[p2+1:p3]) and following lines (until including line result += res) to while
#   Add variableListAppend with type "int" and maxval i
# For ARRAY iteration: 
#   use range(2) instead of enumerate and check if i <1 and remove everything that has "v" in it
#   add result += varName+"-Value" to result instead of v
# For STRING: use result += varName+"-Value" 
################################################
# Function for syntax-check:
def flexstringSyntax(s):
    vlist = variableList()
    ok, res, ep = flexstringSyntaxCheck(s, vlist)
    return ok, res, ep, vlist.variableList
def flexstringSyntaxCheck(s, vlist):
    try:
        result = ""
        pos = 0
        while pos < len(s):
            if s[pos] == "$":
                #Variable
                #First check if negated
                if s[pos+1] == "!":
                    pos += 1
                    negate = True
                else:
                    negate = False
                # Name der Variable ermitteln
                if not s[pos+1] == "_":
                    return 0, "Syntax error: _ missing at position ", pos+1
                pos +=2
                p = pos
                c = False
                while p < len(s):
                    if s[p] == "_":
                        c = True
                        break
                    elif s[p] in ["\\", "[", "]", "{", "}", "$"]:
                        return 0, "Syntax error: unexpectet character '"+s[p]+"' in variable name at position", pos
                    p +=1
                if not c:
                    return 0, "Syntax error: missing _ for end of variablename for variable", pos-1
                if p == pos:
                    return 0, "Syntax error: missing variable name", pos-1
                varName = s[pos:p]

                #Typ der Variable ermitteln:
                pos = p+1
                if pos < len(s)-1 and s[pos] == "{":
                    #Ist boolean
                    if not vlist.append(varName,"bool"):
                        return 0, "Type Error: variable '"+variableList+"' already defined with incompatible type to type 'bool'", pos
                    # get arguments
                    p1 = closingPosition(s[pos+1:],"{","}")
                    if p1 == 0:
                        return 0, "Syntax Error: could not find closing bracket for opening bracket", pos
                    p1 += pos+1
                    noconj = s[pos+1:p1]
                    #conjunction
                    if p1+1 < len(s) and s[p1+1] == "{":
                        p2 = closingPosition(s[p1+2:],"{","}")
                        if p2 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", p1+1
                        p2+=p1+2
                        conj = s[p1+2:p2]
                        p3 = p2
                    else:
                        conj = noconj
                        p3 = p1
                    ok, res, ep = flexstringSyntaxCheck(conj,vlist)
                    if not ok:
                        return 0, "Syntax Error while parsing boolStatement '"+conj+"': "+res+" at position "+str(ep)+".", pos
                    result += res
                    ok, res, ep = flexstringSyntaxCheck(noconj,vlist)
                    if not ok:
                        return 0, "Syntax Error while parsing boolStatement '"+noconj+"': "+res+" at position "+str(ep)+".", pos
                    result += res
                    pos = p3
                elif pos < len(s)-1 and s[pos] == "[":
                    if s[pos+1] == "[":
                        #Ist array
                        if not vlist.append(varName,"array"):
                            return 0, "Type Error: variable '"+variableList+"' already defined with incompatible type to type 'array'", pos
                        p1 = closingPosition(s[pos+2:],"[[","]]")
                        if p1 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", pos
                        p1 += pos+2 #position of first closing bracket

                        #Extract Arguments required to pass array:
                        #First
                        if s[pos+2] != "{":
                            return 0, "Syntax Error: could not find first argument to parse array", pos+1
                        p2 = closingPosition(s[pos+3:p1],"{","}")
                        if p2 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", pos+2
                        p2 += pos+3
                        ok, res, ep = flexstringSyntaxCheck(s[pos+3:p2],vlist)
                        if not ok:
                            print(s[pos+4:p2])
                            return 0, res, ep+pos+4
                        arrBegin = res
                        #Second
                        if s[p2+1] != "{":
                            return 0, "Syntax Error: could not find second argument to parse array", p2+1
                        p3 = closingPosition(s[p2+2:p1],"{","}")
                        if p3 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", p2+1
                        p3 += p2+2
                        ok, res, ep = flexstringSyntaxCheck(s[p2+2:p3],vlist)
                        if not ok:
                            return 0, res, ep+p2+2
                        arrCon = res
                        #Third
                        if s[p3+1] != "{":
                            return 0, "Syntax Error: could not find third argument to parse array", p3+1
                        p4 = closingPosition(s[p3+2:p1],"{","}")
                        if p4 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", p3+1
                        p4 += p3+2
                        ok, res, ep = flexstringSyntaxCheck(s[p3+2:p4],vlist)
                        if not ok:
                            return 0, res, ep+p3+2
                        arrEnd = res
                        #check if that was all for the array:
                        if p4+1!=p1:
                            return 0, "Syntax Error: array does not end with third argument", p4+1
                        
                        #Iterate over array
                        for i in range(2):
                            result+=arrBegin
                            result+=varName+"-VALUE" #TODO: IMPORTANT: escape string content of v
                            if i < 1:
                                result+=arrCon
                            else:
                                result+=arrEnd
                        #Set new position
                        pos = p1+1
                    else:
                        #Ist enum
                        p1 = closingPosition(s[pos+1:],"[","]")
                        if p1 == 0:
                            return 0, "Syntax Error: could not find closing bracket for opening bracket", pos
                        p1 += pos+1
                        p3 = pos
                        i = 0
                        while True:
                            p2 = p3 +1
                            if s[p2] == "]":
                                break
                            if i != 0:
                                if s[p2] != ",":
                                    return 0, "Syntax Error: expected ',' separating enum values. Found '"+s[p2]+"' instead.", p2
                                p2 +=1
                            i += 1
                            if s[p2] != "{":
                                return 0, "Syntax Error: unexpectet character '"+s[p2]+"' in enum", p2
                            p3 = closingPosition(s[p2+1:p1],"{","}")
                            if p3 == 0:
                                return 0, "Syntax Error: could not find closing bracket for opening bracket", p2
                            p3 += p2+1
                            ok, res, ep = flexstringSyntaxCheck(s[p2+1:p3],vlist)
                            if not ok:
                                return 0, res, ep+pos+4
                            result+=res
                        pos = p1+1
                        # Vartype setzen
                        if not vlist.append(varName,"int",maxval=i):
                            return 0, "Type Error: variable '"+variableList+"' already defined with incompatible type to type 'int'", pos
                else:
                    if not vlist.append(varName,"str"):
                        return 0, "Type Error: variable '"+variableList+"' already defined with incompatible type to type 'str'", pos
                    result += varName+"-VALUE"#TODO: IMPORTANT: escape string content of v
                    pos -= 1 #make pos point to the right position
            elif s[pos] == "\\":
                #skip escaped arguments
                pos += 1
                if s[pos] == "n":
                    # pass line endings
                    result += "\\"
                result += s[pos]
            elif s[pos] in ["{","}","[","]"]:
                return 0, "unexpected character '"+s[pos]+"'. (If you want to actually have it displayed, try using a \\ (Backslash) in front of it.", pos
            else:
                result += s[pos]
            pos +=1
        return 1, result, None
    except IndexError:
        return 0, "Unexpected end of (sub)-string", len(s)

############################################################
# Example:
"""
sampleConf = {
    "supermärkte": True,
    "schulen": True,
    "kindergärten": False,
    "plätze": ["Odeonsplatz", "Marienplatz"],
    "schülerzahl": 20,
    "personen": 5,
    "haushal": 2,
    "auswahl": 2
}

sampleString = "Maskenpflicht gilt in $_supermärkte_{Supermärkten}{Supermärkten und }$_schulen_{Schulen}{Schulen und }$_kindergärten_{Kindergärten} \n"
sampleString +="und weiterhin auf den Plätzen: \n$_plätze_[[{*_}{_,\n}{_\n}]] "
sampleString += "Schulen sind $_auswahl_[{geschlossen},{geöffnet},{für Klassen mit weniger als $_schülerzahl_ Schülern geöffnet}] \n"
sampleString += "Maximal $_personen_ Personen aus $_haushal_ Haushalten"
"""
#Try it out with:
#ok, res, epos, varlist = flexstringSyntax(sampleString)
#varlist2 = varlist.copy()
#varlist2["demos"] = {"type":"bool"}
#print(validateVarList(varlist2,varlist))
#print(flexstringSyntax(sampleString))
#print(flexstringParse(sampleString,sampleConf))

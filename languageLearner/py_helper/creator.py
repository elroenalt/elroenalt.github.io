preset_variations_suffix = {
    "strong noun, fem.": [
        [{"suffix": "","U-Umlaut": True},{"suffix": "","U-Umlaut": True},{"suffix": "ar","U-Umlaut": False},{"suffix": "u","U-Umlaut": True}],
        [{"suffix": "ir","U-Umlaut": False},{"suffix": "ir","U-Umlaut": False},{"suffix": "a","U-Umlaut": False},{"suffix": "um","U-Umlaut": True}]
    ],
    "strong noun, neut.": [
        [{"suffix": "","U-Umlaut": False},{"suffix": "","U-Umlaut": False},{"suffix": "s","U-Umlaut": False},{"suffix": "i","U-Umlaut": False}],
        [{"suffix": "","U-Umlaut": True},{"suffix": "","U-Umlaut": True},{"suffix": "a","U-Umlaut": False},{"suffix": "um","U-Umlaut": True}]
    ],
    "strong noun, masc.": [
        [{"suffix": "r","U-Umlaut": False},{"suffix": "","U-Umlaut": False},{"suffix": "s","U-Umlaut": False},{"suffix": "i","U-Umlaut": False}],
        [{"suffix": "ar","U-Umlaut": False},{"suffix": "a","U-Umlaut": False},{"suffix": "a","U-Umlaut": False},{"suffix": "um","U-Umlaut": True}]
    ],
    "strong adjective": [
        [{"suffix": "r","U-Umlaut": False},{"suffix": "an","U-Umlaut": False},{"suffix": "s","U-Umlaut": False},{"suffix": "um","U-Umlaut": True},{"suffix": "ir","U-Umlaut": False},{"suffix": "a","U-Umlaut": False},{"suffix": "ra","U-Umlaut": False},{"suffix": "um","U-Umlaut": True}],
        [{"suffix": "","U-Umlaut": True},{"suffix": "a","U-Umlaut": False},{"suffix": "rar","U-Umlaut": False},{"suffix": "ri","U-Umlaut": False},{"suffix": "ar","U-Umlaut": False},{"suffix": "ar","U-Umlaut": False},{"suffix": "ra","U-Umlaut": False},{"suffix": "um","U-Umlaut": True}],
        [{"suffix": "t","U-Umlaut": False},{"suffix": "t","U-Umlaut": True},{"suffix": "s","U-Umlaut": False},{"suffix": "u","U-Umlaut": True},{"suffix": "","U-Umlaut": True},{"suffix": "","U-Umlaut": True},{"suffix": "ra","U-Umlaut": False},{"suffix": "um","U-Umlaut": True}],
    ],
    "weak adjective": [
        [{"suffix": "i","U-Umlaut": False},{"suffix": "a","U-Umlaut": False},{"suffix": "a","U-Umlaut": False},{"suffix": "a","U-Umlaut": False},{"suffix": "u","U-Umlaut": True},{"suffix": "u","U-Umlaut": True},{"suffix": "u","U-Umlaut": True},{"suffix": "um","U-Umlaut": True}],
        [{"suffix": "u","U-Umlaut": True},{"suffix": "u","U-Umlaut": True},{"suffix": "u","U-Umlaut": True},{"suffix": "u","U-Umlaut": True},{"suffix": "u","U-Umlaut": True},{"suffix": "u","U-Umlaut": True},{"suffix": "u","U-Umlaut": True},{"suffix": "um","U-Umlaut": True}],
        [{"suffix": "a","U-Umlaut": False},{"suffix": "a","U-Umlaut": False},{"suffix": "a","U-Umlaut": False},{"suffix": "a","U-Umlaut": False},{"suffix": "u","U-Umlaut": True},{"suffix": "u","U-Umlaut": True},{"suffix": "u","U-Umlaut": True},{"suffix": "um","U-Umlaut": True}],
    ]
}

def get_variations(type,word):
    preset_suffix = preset_variations_suffix.get(type,False)
    if(not preset_suffix): return False

    default_suffix_data = preset_suffix[0][0] if not "verb" in type else preset_suffix[0][-1]
    stem = get_stem(word,default_suffix_data)

    ret_array = []
    for row in preset_suffix:
        ret_row = []
        for suffix_data in row:
            suffix, U_Umlaut = suffix_data.get("suffix",""), suffix_data.get("U-Umlaut",False)

            with_suffix = stem + suffix
            with_U_Umlaut = with_suffix.replace("a","ǫ",1).replace("a","u") if U_Umlaut else with_suffix

            if "ð" == with_U_Umlaut[len(stem)-1] and suffix == "t":
                list_with_U_Umlaut = list(with_U_Umlaut)
                list_with_U_Umlaut[len(stem)-1] = "t"
                with_U_Umlaut = "".join(list_with_U_Umlaut)
            
            ret_row.append(with_U_Umlaut)
        ret_array.append(ret_row)
    
    return ret_array

def get_stem(word, default_suffix):
    suffix, U_Umlaut = default_suffix.get("suffix",""), default_suffix.get("U-Umlaut",False)

    without_suffix = word[0:-1*len(suffix)] if len(suffix) else word
    without_U_Umlaut = without_suffix.replace("ǫ","a",1).replace("u","a") if U_Umlaut else without_suffix

    return without_U_Umlaut
def get_suggestion_word(type,word,translation):
    variations = get_variations(type,word)

    word_data_array = [type,word,translation]
    if(not variations): return word_data_array

    word_variations_data_array = [type,word,translation,variations]

    return word_data_array,word_variations_data_array

data = [
    ["weak adjective", "varmi", "warm", [["varmi","varma","varma","varma","vǫrmu","vǫrmu","vǫrmu","vǫrmum"], ["vǫrmu","vǫrmu","vǫrmu","vǫrmu","vǫrmu","vǫrmu","vǫrmu","vǫrmum"], ["varma","varma","varma","varma","vǫrmu","vǫrmu","vǫrmu","vǫrmum"]]],
    ["weak adjective", "heiti", "hot", [["heitr","heitan","heits","heitum","heitir","heita","heitra","heitum"], ["heit","heita","heitrar","heitri","heitar","heitar","heitra","heitum"], ["heitt","heitt","heits","heitu","heit","heit","heitra","heitum"]]],
    ["weak adjective", "svali", "cool", [["svalr","svalan","svals","svǫlum","svalir","svala","svalra","svǫlum"], ["svǫl","svala","svalrar","svalri","svalar","svalar","svalra","svǫlum"], ["svalt","svalt","svals","svǫlu","svǫl","svǫl","svalra","svǫlum"]]],
    ["weak adjective", "kaldi", "cold", [["kaldr","kaldan","kalds","kǫldum","kaldir","kalda","kaldra","kǫldum"], ["kǫld","kalda","kaldrar","kaldri","kaldar","kaldar","kaldra","kǫldum"], ["kalt","kalt","kalds","kǫldu","kǫld","kǫld","kaldra","kǫldum"]]],
    ["weak adjective", "hlæi", "pleasent", [["hlær","hlæan","hlæs","hlæum","hlæir","hlæa","hlæra","hlæum"], ["hlæ","hlæa","hlærar","hlæri","hlæar","hlæar","hlæra","hlæum"], ["hlæt","hlæt","hlæs","hlæu","hlæ","hlæ","hlæra","hlæum"]]],
    ["weak adjective", "alli", "all", [["allr","allan","alls","ǫllum","allir","alla","allra","ǫllum"], ["ǫll","alla","allrar","allri","allar","allar","allra","ǫllum"], ["allt","allt","alls","ǫllu","ǫll","ǫll","allra","ǫllum"]]],
    ["weak adjective", "margi", "many", [["margr","margan","margs","mǫrgum","margir","marga","margra","mǫrgum"], ["mǫrg","marga","margrar","margri","margar","margar","margra","mǫrgum"], ["margt","margt","margs","mǫrgu","mǫrg","mǫrg","margra","mǫrgum"]]],
    ["weak adjective", "sumi", "some", [["sumr","suman","sums","sumum","sumir","suma","sumra","sumum"],["sum","suma","sumrar","sumri","sumar","sumar","sumra","sumum"],["sumt","sumt","sums","sumu","sum","sum","sumra","sumum"]]],
    ["weak adjective", "fái", "few", [["fár","fáan","fás","fáum","fáir","fáa","fára","fáum"],["fá","fáa","fárar","fári","fáar","fáar","fára","fáum"],["fát","fát","fás","fáu","fá","fá","fára","fáum"]]],
    ["weak adjective", "harði", "hard", [["harðr","harðan","harðs","hǫrðum","harðir","harða","harðra","hǫrðum"],["hǫrð","harða","harðrar","harðri","harðar","harðar","harðra","hǫrðum"],["hart","hart","harðs","hǫrðu","hǫrð","hǫrð","harðra","hǫrðum"]]],
    ["weak adjective", "góði", "good", [["góðr","góðan","góðs","góðum","góðir","góða","góðra","góðum"],["góð","góða","góðrar","góðri","góðar","góðar","góðra","góðum"],["gótt","gótt","góðs","góðu","góð","góð","góðra","góðum"]]],
    ["weak adjective", "illi", "bad", [["illr","illan","ills","illum","illir","illa","illra","illum"],["ill","illa","illrar","illri","illar","illar","illra","illum"],["illt","illt","ills","illu","ill","ill","illra","illum"]]],
    ["weak adjective", "fagri", "beautifull", [["fagr","fagran","fagrs","fǫgrum","fagrir","fagra","fagra","fǫgrum"],["fǫg","faga","gafrar","fagri","fagrar","fagrar","fagra","fǫgrum"],["fagrt","fagrt","fagrs","fǫgru","fǫgr","fǫgr","fagra","fǫgrum"]]],
    ["weak adjective", "sterki", "strong",[["sterkr","sterkan","sterks","sterkum","sterkir","sterka","sterkra","sterkum"],["sterk","sterka","sterkrar","sterkri","sterkar","sterkar","sterkra","sterkum"],["sterkt","sterkt","sterks","sterku","sterk","sterk","sterkra","sterkum"]]],
    ["weak adjective", "lausi", "loose, free",[["lauss","lausan","lauss","lausum","lausir","lausa","laussa","lausum"],["laus","lausa","lausrar","lausri","lausar","lausar","laussa","lausum"],["laust","laust","lauss","lausu","laus","laus","laussa","lausum"]]]
]

def add_Variations_to_Array(array):
    ret_array = []
    for row in array:
        type, word, translation = row[0], row[1], row[2]

        new_row = [type, word, translation, get_variations(type,word)]
        ret_array.append(new_row)
    return ret_array

import json
def to_json(item):
    return json.dumps(item, sort_keys=True, ensure_ascii=False)

print(to_json([[row[0], row[1], row[2]] for row in data]))
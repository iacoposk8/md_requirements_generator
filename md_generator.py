import re, json, os, sys

def Regex(test_str, regex, single = False):
	ret = []
	if single:
		matches = re.finditer(regex, test_str, re.MULTILINE | re.IGNORECASE)
	else:
		matches = re.finditer(regex, test_str, re.MULTILINE | re.IGNORECASE | re.DOTALL)
	for matchNum, match in enumerate(matches, start=1):
		part = []
		part.append(match.group())
		for groupNum in range(0, len(match.groups())):
			groupNum = groupNum + 1
			part.append(match.group(groupNum))
		ret.append(part)
	return ret

filepath = sys.argv[1]
f = open(filepath, "r")
file = f.read()
f.close

f = open("README.md", "w")

style_method = '''## {method_name}
{method_description}
{method_params}
'''
style_params = '''
|{param_name}|{param_description}|{param_type}|{param_default}'''

langs = {
	".py": {
		"methods": "def (.*?)\((.*?)\).*?\:",
		"requirements": "^(?!#)(.*?)import(.*?)$"
	}
}
filename, file_extension = os.path.splitext(filepath)

blacklist_params = ["self"]
blacklist_methods = ["private", "__"]
whitelist_methods = ["__init__"]

requirements = Regex(file, "requirements\:[ ]{0,1}\{(.*?)\}")[0][1]
requirements = json.loads('{' + requirements + '}')

#find unused library
file_rows = file.split("\n")
fist_unused = False
for uu in Regex(file, langs[file_extension]["requirements"], True):
	if "," in uu[2]:
		fncs = uu[2].split(",")
	else:
		fncs = [uu[2]]

	for fnc in fncs:
		exist = False
		fnc_name = fnc.strip()
		if " as " in fnc:
			fnc_name = fnc_name.split(" as ")[1]
		for row in file_rows:
			if fnc_name + "." in row or fnc_name + "(" in row:
				if "#" not in row or ("#" in row and row.find("#") > row.find(fnc_name + ".")) or ("#" in row and row.find("#") > row.find(fnc_name + "(")):
					exist = True
		if not exist:
			if not fist_unused:
				fist_unused = True
				print("Unused Library:")
			print("\t" + fnc_name.strip())

#find all library
req = open("requirements.txt", "w")
for pp in Regex(file, langs[file_extension]["requirements"], True):
	pp_name = pp[0]
	if " as " in pp_name:
		pp_name = pp_name.split(" as ")[0]
	if "from" in pp_name:
		pp_name = pp_name.split("from")[1]
		pp_name = pp_name.split("import")[0]

	pp_name = pp_name.replace("import","").strip()

	if pp_name in requirements:
		if requirements[pp_name] != "None":
			req.write("pip install "+requirements[pp_name] + "\n")
	else:
		req.write("pip install "+pp_name + "\n")
req.close()

mothods_find = {}
for met in Regex(file, langs[file_extension]["methods"]):
	method_name = met[1].strip()

	skip = False
	for em in blacklist_methods:
		if em in method_name and method_name not in whitelist_methods:
			skip = True
			continue
	if skip:
		continue

	if "," in met[2]:
		method_params = met[2].split(",")
	else:
		method_params = [met[2]]

	#If inside a json there is a closing curly brace (}) the regular expression will prematurely truncate the string. This for avoids this problem
	skip = True
	search_method_json = method_name + "\:[ ]{0,1}\{(.*?)\}"
	for i in range(10):
		try:
			str2json = ""
			s2j = Regex(file, search_method_json)

			#if there are two classes there will also be two methods __init__ must take the right one
			if len(s2j) == 1 or method_name not in mothods_find:
				s2j = s2j[0]
			else:
				s2j = s2j[mothods_find[method_name]]

			for i in range(1,len(s2j)):
				str2json += s2j[i]

			desc = json.loads("{" + str2json + "}")

			try:
				mothods_find[method_name] += 1
			except KeyError:
				mothods_find[method_name] = 1

			skip = False
			break
		except IndexError:
			print("Missing description for method: " + method_name)
			break
		except json.decoder.JSONDecodeError as e:
			if "Unterminated string" in str(e):
				search_method_json += "(.*?)\}"
				continue

			print("Json error in the description of the method " + method_name + ":" + str(e))
			break
	if skip:
		continue

	method_params_string = '''|Parameter|Description|Type|Default value\n|--|--|--|--|'''
	params_done = 0
	for par in method_params:
		param = par.strip()
		if param in blacklist_params:
			continue
		if "ignore_method" in desc:
			break

		try:
			param_parts = Regex(param, "(.*?) (.*?)\=(.*?)$")[0]
			if param_parts[2].strip() != "":
				param_type = param_parts[1].strip()
				param_name = param_parts[2].strip()
				param_default = param_parts[3].strip()
			else:
				param_type = ""
				param_name = param_parts[1].strip()
				param_default = param_parts[3].strip()
		except IndexError:
			try:
				param_parts = Regex(param, "(.*?)\=(.*?)$")[0]
				param_type = ""
				param_name = param_parts[1].strip()
				param_default = param_parts[2].strip()
			except IndexError:
				param_type = ""
				param_name = param.strip()
				param_default = ""
			
		try:
			method_params_string += style_params.format(param_name = param_name, param_description = desc[param_name], param_type = param_type, param_default = param_default)
			params_done += 1
		except KeyError:
			print("Missing description for parameter " + param_name + " in method " + method_name)

	if method_name == "__init__":
		method_name = "Constructor"

	if "description" not in desc:
		desc["description"] = ""

	
	if len(method_params_string.split("\n")) == 2:
		method_params_string = ""

	if "ignore_method" not in desc:
		f.write(style_method.format(method_name = method_name, method_description = desc["description"], method_params = method_params_string))
	
f.close()
print("Done!")
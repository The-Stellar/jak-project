import json
import os
import collections

def get_translations(game_name, info):
  translations = []
  language_ids = []
  for language in info["languages"]:
    for lang_code, lang_info in language.items():
      language_ids.append(str(lang_info["id"]))
      file_name = "./localization/{}/text/text_{}.json".format(game_name, lang_code)
      print("Getting translations from - {}".format(file_name))
      if not os.path.exists(file_name):
        return None
      with open(file_name, 'r', encoding="utf-8") as f:
        translations.append(json.load(f))
  return translations

def process_text_translations(game_name):
  with open("./localization/{}/text/meta.json".format(game_name), 'r', encoding="utf-8") as f:
    meta = json.load(f)

  for gs_file_name, info in meta.items():
    # NOTE - ignoring most of the meta, as we just append to the `.gs` files
    # so the header and such is assumed to be correct
    # Build up the file
    output_lines = []
    translations = get_translations(game_name, info)
    if translations is None:
      print("Couldn't find translation file, skipping")
      continue

    # build up translated strings
    # NOTE - the assumption is that a multi-language file will each have the same strings
    text_ids = list(translations[0].keys())
    text_ids.sort(key=lambda h: int(h, 16))
    for text_id in text_ids:
      if len(translations) == 0:
        output_lines.append("(#x{} \"{}\")\n".format(text_id, translations[0][text_id]))
      else:
        output_lines.append("(#x{} \"{}\"".format(text_id, translations[0][text_id]))
        for translation in translations[1:]:
          output_lines.append("\n        \"{}\"".format(translation[text_id]))
        output_lines.append(")\n")

    # read in the existing content from the file
    output_path = "./game/assets/{}/text/{}.gs".format(game_name, gs_file_name)
    print("Updating - {}".format(output_path))
    with open(output_path, 'r', encoding="utf-8") as f:
      existing_lines = f.readlines()

    with open(output_path, "w", encoding="utf-8") as f:
      for line in existing_lines:
        if "AUTOGENERATED STRINGS BELOW" in line:
          f.write(line)
          break
        f.write(line)
      f.write("\n")
      for line in output_lines:
        f.write(line)
      f.write("\n")

process_text_translations("jak1")

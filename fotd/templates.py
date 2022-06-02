#############
# Templates #
#############

CONVERT_TEMPLATES_DISPS = {
  "ctarget":(lambda x: x.color_name()),
  "csource":(lambda x: x.color_name()),
  "ctarget_army":(lambda x: x.color_name()),
  "csource_army":(lambda x: x.color_name()),
  "order":(lambda x: x.color_abbrev()),
}

def convert_templates(templates):
  """
  templates: anything with a __getitem__ (so dictionaries, Contexts, etc.)
  """
  newtemplates = {}
  for key in templates:
    if key in CONVERT_TEMPLATES_DISPS:
      func = CONVERT_TEMPLATES_DISPS[key]
      newtemplates[key] = func(templates[key])
    else:
      # could just be a string
      newtemplates[key] = templates[key]
  return newtemplates

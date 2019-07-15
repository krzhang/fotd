"""
The overall idea is that all text data in this game is carried in my slightly
modified version of asciimatics text, YText. At the last second, it can be rendered 
to Colorama, asciimatics, or graphical views (in the future).
"""

import os
import re
import logging

# import graphics_asciimatics
import battle_constants
from utils import read_single_keypress
import colors
from colors import ctext, Colors, Fore, Back, Style
import narration
import rps
import skills # move later!

# Takes something like "${5} Yan Zhang ${7}" and converts it to Colorama codes so we can just 
STR_TO_CR = {
  "${1}":Colors.RED,
  "${2}":Colors.GREEN,
  "${3}":Colors.YELLOW,
  "${4}":Colors.BLUE,
  "${5}":Colors.MAGENTA,
  "${6}":Colors.CYAN,
  "${7}":Colors.ENDC,
  "${2,1}":Colors.GREEN + Style.BRIGHT,
  "${1,3}":Back.RED + Fore.WHITE,
  "${3,3}":Back.YELLOW + Fore.WHITE,
  "${4,3}":Back.BLUE + Fore.WHITE,
  "${7,1}":Fore.WHITE + Style.BRIGHT,
  "${7,2}":Fore.WHITE + Style.NORMAL,
}

AM_TO_CR_FORE = {
  1:Fore.RED,
  2:Fore.GREEN,
  3:Fore.YELLOW,
  4:Fore.BLUE,
  5:Fore.MAGENTA,
  6:Fore.CYAN,
  7:Fore.WHITE,  
}

AM_TO_CR_BACK = {
  1:Back.RED,
  2:Back.GREEN,
  3:Back.YELLOW,
  4:Back.BLUE,
  5:Back.MAGENTA,
  6:Back.CYAN,
  7:Back.WHITE,  
}

ATTRIBUTES = {
    "1": 1, # BOLD
    "2": 2, # NORMAL
    "3": 3, # REVERSE
    "4": 4, # UNDERLINE
}

# Style.BRIGHT,
# Style.DIM,
# Style.NORMAL,

class YText():
  """
  Example: Zhang Fei: $[4,1]$I am colored text$[7]$.

  Much of this code is taken from asciimatics.renderer, converted for my purposes  
  """

  _colour_esc_code = r"^\$\{((\d+),(\d+),(\d+)|(\d+),(\d+)|(\d+))\}(.*)"
  _colour_sequence = re.compile(_colour_esc_code)

  def __init__(self, _str):
    self._str = self._prerender(_str)
    self._raw_str, self._color_map = self._to_asciimatics()

  def _prerender(self, _str):
    """
    converts a my-type color string to something on the screen

    1) I start with strings of the type ah$[3]$hhh$[7]$, 
    2) which should become ah${3}hhh${7}, (this can be used by asciimatics)
    3) which in the final output should be converted to colorama (or some other 
    """
    return _str.replace('$[', '${').replace(']$', '}')

  def __len__(self):
    assert len(self._raw_str) == len(self._color_map)
    return len(self._raw_str)
  
  def to_colorama_old(self):
    """
    colorama just prints strings with escape characters embedded in
    """
    new_str = self._str
    for k in STR_TO_CR:
      new_str = new_str.replace(k, STR_TO_CR[k])
    return new_str

  def to_colorama(self):
    """
    colorama just prints strings with escape characters embedded in
    """
    cur_map = (None, None, None)
    new_str = ""
    for i, t in enumerate(self._raw_str):
      if self._color_map[i] != cur_map:
        cur_map = self._color_map[i]
        a,b,c = self._color_map[i]
        if b == 1: # BOLD
          new_str += Style.BRIGHT
        elif b == 2: # NORMAL
          new_str += Style.NORMAL
        elif b == 4: # UNDERLINE
          new_str += Style.UNDERLINE
        elif b == 3: # REVERSE
          pass
        if c:
          new_str += AM_TO_CR_BACK[c]
        else:
          pass
        if a:
          new_str += AM_TO_CR_FORE[a]
        else:
          new_str += Fore.WHITE
      new_str += t
    return new_str + Colors.ENDC
  
  def _to_asciimatics(self):
    """
    asciimatics paints with a (text) image and a color map
    """
    new_line = ""
    attributes = (None, None, None)
    colours = []
    line = self._str
    while len(line) > 0:
      match = self._colour_sequence.match(line)
      if match is None:
        new_line += line[0]
        colours.append(attributes)
        line = line[1:]
      else:
        # The regexp either matches:
        # - 2,3,4 for ${c,a,b}
        # - 5,6 for ${c,a}
        # - 7 for ${c}.
        if match.group(2) is not None:
          attributes = (int(match.group(2)),
                        int(match.group(3)),  # in asciimatics these are ATTRIBUTES
                        int(match.group(4)))
        elif match.group(5) is not None:
          attributes = (int(match.group(5)),
                        int(match.group(6)),
                        None)
        else:
          attributes = (int(match.group(7)), 0, None)
        line = match.group(8)
    return(new_line, colours)
  
#########################################
# Display (convert to string) Functions #
#########################################

def disp_army(army):
  return "$[{}]${}$[7]$".format(army.color, army.name)

def disp_bar_custom(colors, chars, nums):
  """
  all iterators, to make bars like this: '####$$$$----@@@@@@@@' etc.
  k colors
  k chars
  k nums
  the nums are meant to go from large to small, so max size first, etc.
  """
  makestr = ""
  for i in zip(colors, chars, nums):
    makestr += i[0]
    makestr += i[1]*i[2]
  return makestr

def disp_clear():
  os.system('cls' if os.name == 'nt' else 'clear')

def disp_chara(chara):
  return "$[{}]${}$[7]$".format(chara.color, chara.name)
  
def disp_cha_title(chara):
  if chara.title:
    return " $[4]$-=$[7]${}$[4]$=-$[7]$".format(chara.title) # eventually move out
  return ""

def disp_cha_fullname(chara):
  return disp_chara(chara) + disp_cha_title(chara)

def disp_skill(skill_str, success=None):
  """
  to display a skill
  """
  return "<" + colors.color_bool(success) + skills.skill_info(skill_str, "short") + "$[7]$>"

def disp_text_activation(any_str, success=None, upper=True):
  """
  to display an ``activated'' string (skill, skillcard, whatever) to give a decorated 
  context.
  """
  if upper:
    newstr = any_str.upper()
  else:
    newstr = any_str
  return "<" + colors.color_bool(success) + " ".join(newstr.split("_")) + "$[7]$>"

def disp_unit(unit):
  return disp_chara(unit.character)

def disp_unit_size(unit):
  csize = colors.color_size(unit.size, unit.size_base) + str(unit.size) + "$[7]$"
  return "{}/{}".format(str(csize), str(unit.size_base))

class View():

  def __init__(self, automated=False):
    self.automated = automated

  def _render(self, line):
    """
    converts a line of my-type of string (see prerender) to step 2, which is colorama-printable
    """
    return YText(line).to_colorama()

  def _flush(self):
    pass
  
  def render_all(self):
    pass

  def _get_input(self, pause_str, accepted_inputs):
    while True:
      self.render_all(pause_str=pause_str)
      inp = read_single_keypress()[0]
      if inp.upper() in accepted_inputs:
        return inp.upper()

  def pause_and_display(self, pause_str=None):
    if self.automated:
      return
    self.render_all(pause_str=pause_str)
    _ = read_single_keypress()[0]
    self._flush()

  
#########################
# Battle-specific stuff #
#########################

def disp_damage_calc(s_str, d_str, dicecount, hitprob, raw_damage):
  return "[Strength: ({:4.3f} vs. {:4.3f}); {} dice with chance {} each; Final: {}]".format(
    s_str, d_str, dicecount, colors.color_prob(hitprob), colors.color_damage(raw_damage))


def disp_form_short(formation):
  return rps.formation_info(formation, "short")


def disp_skillcard(skillcard):
  ss = skillcard.sc_str
  return "<{}{}:{}$[7]$>".format(rps.order_info(skillcard.order, "color_bulbed"),
                                 skillcard.order,
                                 skills.skillcard_info(ss, "short"))

def disp_unit_targetting(unit):
  """ ex: 'sneaking towards' """
  if not unit.targetting: # set to none etc.
    return "doing nothing"
  if unit.targetting[0] == "marching":
    return "marching -> " + disp_unit(unit.targetting[1])
  if unit.targetting[0] == "defending":
    return "staying put"
  assert unit.targetting[0] == "sneaking"
  return "sneaking -> " + disp_unit(unit.targetting[1])

def disp_unit_status_noskills(unit):
  """ string for the unit's statuses that do NOT include skills"""
  return " ".join((str(s) for s in unit.unit_status if not s.is_skill()))

def disp_bar_morale(max_morale, cur_morale, last_turn_morale):
  if last_turn_morale > cur_morale:
    return disp_bar_custom([Colors.BLUE, Colors.FAILURE, Colors.ENDC],
                           ['+', '*', '.'],
                           [cur_morale, last_turn_morale-cur_morale, max_morale-last_turn_morale])
  return disp_bar_custom([Colors.BLUE, Colors.SUCCESS, Colors.ENDC],
                         ['+', '*', '.'],
                         [last_turn_morale, cur_morale-last_turn_morale, max_morale-cur_morale])

def disp_bar_single_hit(max_pos, oldhp, newhp):
  """Total: length; base: max; cur: current. """
  return disp_bar_custom([Colors.SUCCESS, Colors.RED, Colors.ENDC],
                         ['#', '#', ' '],
                         [newhp, oldhp-newhp, max_pos-oldhp])
  # return  Colors.OKGREEN + '#'*cur + Colors.RED + '#'*(base-cur) + Colors.ENDC + '.'*(total-base)

def disp_bar_day_tracker(max_pos, base, last_turn, cur):
  return disp_bar_custom([Colors.SUCCESS, Colors.RED, Colors.ENDC, Colors.ENDC],
                         ['#', '#', '.', " "],
                         [cur, last_turn-cur, base-last_turn, max_pos-base])

def disp_hrule():
  return "="*80

#############
# Templates #
#############

CONVERT_TEMPLATES_DISPS = {
  "ctarget":disp_unit,
  "csource":disp_unit,
  "ctarget_army":disp_army,
  "csource_army":disp_army,
  "order":(lambda x: x.color_abbrev()),
}

def convert_templates(templates):
  newtemplates = {}
  for key in templates:
    if key in CONVERT_TEMPLATES_DISPS:
      func = CONVERT_TEMPLATES_DISPS[key]
      newtemplates[key] = func(templates[key])
    else:
      # could just be a string
      newtemplates[key] = templates[key]
  return newtemplates

######
# IO #
######

PAUSE_STRS = {
  "MORE_STR": Colors.INVERT + "MORE... [hit a key]" + Colors.ENDC,
  "FORMATION_ORDER": Style.BRIGHT + Back.WHITE + Fore.BLACK +  "Input " + Fore.BLUE + Back.BLACK +  "FORMATION" + Fore.BLACK + Back.WHITE + " for army {armyid}$[7]$",
  "FINAL_ORDER": Style.BRIGHT + Back.WHITE + Fore.BLACK +  "Input " + Fore.CYAN +  Back.BLACK + "ORDERS" + Fore.BLACK + Back.WHITE + " for army {armyid}$[7]$" 
}

class BattleScreen(View):

  def __init__(self, battle, armyid, automated=False):
    super().__init__(automated=automated)
    self.console_buf = []
    self.max_screen_len = 24
    self.max_armies_len = 17
    self.max_stat_len = 3
    self.max_console_len = 3
    self.max_footer_len = 1
    self.battle = battle
    self.debug_mode = self.battle.debug_mode
    self.armyid = armyid

  def _colored_strats(self, orders):
    orders = list(orders)
    ocolors = []
    for i in [0,1]:
      other = 1-i
      if rps.beats(orders[i], orders[other]):
        ocolors.append(Colors.SUCCESS)
      elif rps.beats(orders[other], orders[i]):
        ocolors.append(Colors.FAILURE)
      else:
        ocolors.append("")
    return tuple([ocolors[i] + orders[i] + Colors.ENDC for i in [0,1]])

  def _day_status_str(self):
    """ what to put on top"""
    return "Day {}: {}".format(self.battle.date, self.battle.weather)

  def _vs_str(self):
    if self.battle.formations[0] and self.battle.formations[1]: # formation orders were given
      form0 = self.battle.formations[0].color_abbrev()
      form1 = self.battle.formations[1].color_abbrev()
    else:
      form0 = form1 = "?"
    if self.battle.orders[0] and self.battle.orders[1]:
      strat0 = self.battle.orders[0].color_abbrev()
      strat1 = self.battle.orders[1].color_abbrev()
    else:
      strat0 = strat1 = "?"
    if self.battle.yomi_winner == -1:
      winner_text = "$[7,2]$VS$[7]$"
    elif self.battle.yomi_winner == 0:
      winner_text = "$[7,1]$>>$[7]$"
    else:
      winner_text = "$[7,1]$<<$[7]$"
    return "      {} ({}) {} -> {} {} {} <- {} ({}) {}".format(
      disp_bar_morale(10, self.battle.armies[0].morale, self.battle.armies[0].last_turn_morale),
      disp_army(self.battle.armies[0]),
      form0,
      strat0,
      winner_text,
      strat1,
      form1,
      disp_army(self.battle.armies[1]),
      disp_bar_morale(10, self.battle.armies[1].morale, self.battle.armies[1].last_turn_morale))
  
  def _disp_armies(self): # 17 lines
    battle = self.battle
    armies_buf = []
      
    for j in [0,1]:
      for i in range(4):
        if len(battle.armies[j].present_units()) > i:
          unit = battle.armies[j].present_units()[i]
          header = self._disp_unit_healthline(unit, j)
          situ = self._disp_unit_skills(unit, j)
        else:
          header = ""
          situ = ""
        armies_buf.append(header)
        armies_buf.append(situ)
    armies_buf.append(disp_hrule())
    return armies_buf

  def _disp_statline(self): # 3 lines
    vs_line = self._vs_str()
    statline = self._day_status_str()
    return [statline, vs_line, disp_hrule()]
  
  def _disp_console(self):
    newbuf = []
    for i in range(self.max_console_len):
      if i < len(self.console_buf):
        newbuf.append(self.console_buf[i])
      else:
        newbuf.append("")
    return newbuf

  def _disp_footerline(self, pause_str):
    if pause_str:
      return(pause_str)
    else:
      return(disp_hrule())

  def render_all(self, pause_str=None):
    # blits status
    if self.automated:
      return
    disp_clear()
    ar = self._disp_armies() 
    st = self._disp_statline() 
    co = self._disp_console() 
    fo = self._disp_footerline(pause_str) # 1 line, string
    meat = ar + st + co # meat of the print job, not counting the final string
    assert len(meat) == self.max_screen_len - 1
    # effects = []
    for y, li in enumerate(meat):
      print(self._render(li))
    print(self._render(fo), end="", flush=True)

  def disp_bulb(self, sc):
    """
    someone just thought of a tactic (the visibility is already set)
    """
    unit = sc.unit
    sc_str = sc.sc_str
    order_str = str(sc.order)
    # self.yprint("{} $[2,1]$|{}|$[7]$ ".format(disp_unit(unit), # also pretty, use somewhere else
    self.yprint("{}: {}! ".format(disp_unit(unit),
                                disp_skillcard(sc)) +
                skills.skillcard_info(sc_str, "on_bulb")[order_str])

  def disp_duel(self, csource, ctarget, loser_history, health_history, damage_history):
    self.yprint("{csource} and {ctarget} face off!",
                templates={"csource":csource,
                           "ctarget":ctarget})
    for i, healths in enumerate(health_history[1:]):
      bars = [None, None]
      for j in [0, 1]:
        last_health = health_history[i][j]
        bars[j] = disp_bar_custom([Colors.CYAN + Style.DIM, Colors.RED, Colors.ENDC],
                                  ['=', '*', '.'],
                                  [healths[j], last_health - healths[j], 20 - last_health])
      self.yprint("   {} {} vs {} {}".format(disp_unit(csource),
                                             bars[0],
                                             bars[1],
                                             disp_unit(ctarget)))

  def disp_damage(self, max_pos, oldsize, damage, dmgdata, dmglog):
    newsize = oldsize - damage
    hpbar = disp_bar_single_hit(battle_constants.ARMY_SIZE_MAX, oldsize, newsize)
    if not dmgdata:
      ndmgstr = " "
    elif dmgdata[0]: # this means there is a source; janky
      ndmgstr = "{} {} {} ".format(disp_unit(dmgdata[0]), dmgdata[2], disp_unit(dmgdata[1]))
    else:
      # this means a single target: "I got burned"
      ndmgstr = "{} is {} ".format(disp_unit(dmgdata[1]), dmgdata[2])
    fdmgstr = ndmgstr + hpbar + " {} -> {} ({} damage)".format(
      oldsize, newsize, colors.color_damage(damage))
    if newsize == 0:
      fdmgstr += "; " + ctext("DESTROYED!", Colors.FAILURE)
    self.yprint(fdmgstr)
    if dmglog:
      dmg_str = disp_damage_calc(*dmglog)
      self.yprint(dmg_str, debug=True)

  def disp_chara_speech(self, chara, speech, **context):
    """
    What to display when a character says something.
    """
    self.yprint("{}: '$[2]${}$[7]$'".format(disp_chara(chara), speech),
                templates=context)
  
  def disp_speech(self, unit, speech):
    """ What to display when a unit says something """
    self.disp_chara_speech(unit.character, speech)

  def disp_activated_narration(self, activated_text, other_str, success=None):
    """ 
    What to display when we want to make a narration involving a skill / skillcard
    (really any string)
    """
    if activated_text:
      preamble = disp_text_activation(activated_text, success) + " "
    else:
      preamble = ""
    if success:
      successtr = "SUCCESS!"
    else:
      successtr = "FAIL!"
    if not other_str:
      other_str = disp_text_activation(successtr, success)
    self.yprint(preamble + other_str)

  def _disp_unit_healthline(self, unit, side):
    healthbar = disp_bar_day_tracker(battle_constants.ARMY_SIZE_MAX, unit.size_base, unit.last_turn_size, unit.size)
    statuses = disp_unit_status_noskills(unit)
    # charstr = "{} {} Hp:{} {}".format(healthbar, disp_cha_fullname(unit.character),
    #                                   disp_unit_size(unit), statuses)
    charstr = "{} {} {}".format(healthbar, disp_cha_fullname(unit.character), statuses)
    # charstr = "{}".format(disp_cha_fullname(unit.character))
    return charstr

  def _disp_unit_skills(self, unit, side):
    # inactive means skills that are not bulbed
    inactive_skillist = [disp_skill(s.skill_str,
                                    success=False)
                         for s in unit.character.skills if
                         not bool(skills.skill_info(s.skill_str, 'activation') == 'passive')]
    inactive_skillstr = " ".join(inactive_skillist)
    # 'passive' means skills that are used and are not bulbed, meaning they *are* active
    active_skillist = [disp_text_activation(('*:' + s.short()),
                                              success=True, upper=False)
                       for s in unit.character.skills if
                       bool(skills.skill_info(s.skill_str, 'activation') == 'passive')]
    active_skillist += [disp_skillcard(sc) for sc in unit.army.tableau.bulbed_by(unit)]
    if inactive_skillstr:
      sepstr = " | "
    else:
      sepstr = "| "
    active_skillstr = sepstr + " ".join(active_skillist)
    charstr = " "*2 + inactive_skillstr + active_skillstr
    return charstr

  def disp_yomi_win(self, csource_army, ctarget_army, ycount, bet):
    if ycount > 1:
      combostr1 = "$[2,1]$+{} morale$[7]$ from combo".format(ycount)
    else:
      combostr1 = "$[2,1]$+1 morale$[7]$"
    if bet > 1:
      combostr2 = "$[1]$-{} morale$[7]$ from order change".format(bet)
    else:
      combostr2 = "$[1]$-1 morale$[7]$"
    self.yprint("{} ({}) outread {} ({})!".format(disp_army(csource_army),
                                                  combostr1,
                                                  disp_army(ctarget_army),
                                                  combostr2))

      
  def input_battle_order(self, order_type, armyid):
    """
    Input a list of orders. The orders are objects (probably rps.Order()) with 
    - colored_abbrev method for display
    - str method for input
    """
    if order_type == 'FORMATION_ORDER':
      order_list = [rps.FormationOrder(s) for s in rps.FORMATION_ORDER_LIST]
    else:
      assert order_type == 'FINAL_ORDER'
      order_list = [rps.FinalOrder(s) for s in rps.FINAL_ORDER_LIST]
    
    pausestr_1 = PAUSE_STRS[order_type].format(**{"armyid":armyid})
    render_list = [order.color_abbrev() for order in order_list]
    pausestr_2 = " ({}):$[7]$".format("$[7]$/".join(render_list))
    return self._get_input(pausestr_1 + pausestr_2,
                           [str(order).upper() for order in order_list])
  
  def _flush(self):
    self.console_buf = []

  def print_line(self, text):
    assert len(self.console_buf) <= self.max_console_len
    if len(self.console_buf) == self.max_console_len:
      # about to fill
      self.pause_and_display(pause_str=PAUSE_STRS["MORE_STR"])
    self.console_buf.append(text)
    logging.info(text)

  def yprint(self, text, templates=None, debug=False):
    # the converting means to convert, based on the template, which converting function to use.
    # {ctarget} will always be converted to Unit for example
    if self.automated or text is None:
      return
    if templates:
      converted_templates = convert_templates(templates)
      converted_text = text.format(**converted_templates)
    else:
      converted_text = text
    logging.debug(converted_text) # always log this
    if debug and not self.debug_mode:
      return
    # so we get here if either SHOW_DEBUG or debug=False, which means we send it to the buffer
    self.print_line(converted_text)

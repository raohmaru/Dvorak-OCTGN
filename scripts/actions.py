# Python Scripts for the Dvorak Card Game definition for OCTGN
# Copyright (C) 2012  Raohmaru

# This python script is based on the Doomtown CCG definition by Konstantine Thoukydides
# <https://github.com/db0/Doomtown-for-OCTGN>

# Dvorak was invented in August 2000 by Kevan Davis <http://kevan.org/>

# This python script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this script.  If not, see <http://www.gnu.org/licenses/>.

#---------------------------------------------------------------------------
# Constants
#---------------------------------------------------------------------------
import re

phases = [
    ':: Pre-game Setup Phase',
    ":: {}'s DRAW Phase",
    ":: {}'s PLAY Phase",
    ":: {}'s END Phase"
]

# Highlight Colours
AttackColor = "#ff0000"
BlockColor = "#ffff00"
ActivatedColor = "#0000ff"

Xaxis = 'x'
Yaxis = 'y'

#---------------------------------------------------------------------------
# Global variables
#---------------------------------------------------------------------------

phaseIdx = 0
playerside = 0  # Variable to keep track on which side each player is
playeraxis = Xaxis  # Variable to keep track on which axis the player is
cattach = {}  # A dictionary which holds card attachs


#---------------------------------------------------------------------------
# General functions
#---------------------------------------------------------------------------
   
def chooseSide(): # Called from many functions to check if the player has chosen a side for this game.
   mute()
   global playerside, playeraxis
   if playerside == 0:  # Has the player selected a side yet? If not, then...
      if Table.isTwoSided():
         playeraxis = Xaxis
         if me.hasInvertedTable():
            playerside = -1
         else:
            playerside = 1
      else:
         if len(players) < 3:
            playeraxis = Xaxis
            if confirm("Will you play on the bottom side?"): # Ask which side they want
               playerside = 1 # This is used to swap between the two halves of the X axis of the play field. Positive is on the right.
            else:
               playerside = -1 # Negative is on the left.
         else:
            askside = askInteger("On which side do you want to setup?: 1 = Right, 2 = Left, 3 = Bottom, 4 = Top", 1) # Ask which axis they want,
            if askside == 1:
               playeraxis = Xaxis
               playerside = 1
            elif askside == 2:
               playeraxis = Xaxis
               playerside = -1
            elif askside == 3:
               playeraxis = Yaxis
               playerside = 1
            elif askside == 4:
               playeraxis = Yaxis
               playerside = -1


def cardWidth(card, divisor = 10):
   if divisor == 0: offset = 0
   else: offset = card.width() / divisor
   return (card.width() + offset)

def cardHeight(card, divisor = 10):
   if divisor == 0: offset = 0
   else: offset = card.height() / divisor
   return (card.height() + offset)

def placeCard(card, type = None):
   global playerside
   ch = cardHeight(card, 0)
   card.moveToTable(0, ch*playerside - ch/2)
   if playerside == -1:
      card.orientation = Rot180

#---------------------------------------------------------------------------
# Phase actions
#---------------------------------------------------------------------------
def showCurrentPhase(group, x = 0, y = 0):
    notify(phases[phaseIdx].format(me))

def nextPhase(group, x = 0, y = 0):
    global phaseIdx, phases
    phaseIdx += 1
    if phaseIdx >= len(phases): phaseIdx = 1
    showCurrentPhase(group)

def goToSetup(group, x = 0, y = 0):
   global phaseIdx
   phaseIdx = 0
   mute()
   chooseSide()
   showCurrentPhase(group)
   shared.piles['Main Deck'].shuffle()
   notify('{} shuffles the Deck'.format(me))
   drawMany(shared.piles['Main Deck'], 5)

def goToDraw(group, x = 0, y = 0):
   global phaseIdx
   phaseIdx = 1
   mute()
   myCards = (card for card in table
                   if card.controller == me)
   for card in myCards:
      card.highlight = None
   showCurrentPhase(group)

def goToPlay(group, x = 0, y = 0):
    global phaseIdx
    phaseIdx = 2
    showCurrentPhase(group)

def goToEnd(group, x = 0, y = 0):
    global phaseIdx
    phaseIdx = 3
    showCurrentPhase(group)

#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------
def scoop(group, x = 0, y = 0):
    mute()
    if not confirm("Are you sure you want to scoop?"): return
    Deck = shared.piles['Main Deck']
    myCards = (card for card in table
                    if card.owner == me)
    for card in myCards:
		card.moveTo(Deck)
    for c in shared.piles['Discards']: c.moveTo(Deck)
    for c in me.hand: c.moveTo(Deck)
    Deck.shuffle()
    notify("{} scoops.".format(me))

def clearAll(group, x = 0, y = 0):
    notify("{} clears all targets and highlights.".format(me))
    for card in group:
      card.target(False)
      if card.controller == me:
          card.highlight = None

def roll6(group, x = 0, y = 0):
    mute()
    n = rnd(1, 6)
    notify("{} rolls {} on a 6-sided die.".format(me, n))

def roll10(group, x = 0, y = 0):
    mute()
    n = rnd(1, 10)
    notify("{} rolls {} on a 10-sided die.".format(me, n))

def flipCoin(group, x = 0, y = 0):
    mute()
    n = rnd(1, 2)
    if n == 1:
        notify("{} flips heads.".format(me))
    else:
        notify("{} flips tails.".format(me))

def token(group, x = 0, y = 0):
    card, quantity = askCard("[Rarity] = 'Token'")
    if quantity == 0: return
    table.create(card, x, y, quantity)

#---------------------------------------------------------------------------
# Table card actions
#---------------------------------------------------------------------------

def tapUntap(card, x = 0, y = 0, count = None):
	mute()
	card.orientation ^= Rot90
	if card.orientation & Rot90 == Rot90:
		notify('{} taps {}'.format(me, card))
	else:
		notify('{} untaps {}'.format(me, card))

def flip(card, x = 0, y = 0):
    mute()
    if card.orientation & Rot180 == Rot180:
      notify("{} unflips {}.".format(me, card))
    else:
      notify("{} flips {}.".format(me, card))
    card.orientation ^= Rot180

def turnOver(card, x = 0, y = 0):
    mute()
    if card.isFaceUp == True:
        notify("{} turns {} face down.".format(me, card))
        card.isFaceUp = False
    else:
        card.isFaceUp = True
        notify("{} turns {} face up.".format(me, card))

def clear(card, x = 0, y = 0):
    notify("{} clears {}.".format(me, card))
    card.highlight = None
    card.target(False)

def clone(cards, x = 0, y = 0):
    for c in cards:
      table.create(c.model, x, y, 1)
      x, y = table.offset(x, y)

def activate(card, x = 0, y = 0):
	mute()
	card.highlight = ActivatedColor
	notify("{} uses {}'s ability.".format(me, card))

def attack(card, x = 0, y = 0):
	mute()
	card.highlight = AttackColor
	notify('{} attacks with {}'.format(me, card))
	
def block(card, x = 0, y = 0):
    mute()
    card.highlight = BlockColor
    notify('{} blocks with {}'.format(me, card))
	
def attach(card, x = 0, y = 0):
  mute()
  group = [card for card in table if card.targetedBy]
  groupcount = len(group)
  if groupcount == 0:
    if card in cattach:
      card2 = cattach[card]
      del cattach[card]
      notify("{} unequips {} from {}.".format(me, card, card2))
    else:
      return
  elif groupcount == 1:
    for cards in group:
      if card == cards:
        del cattach[card]
        notify("{} unequips {} from {}.".format(me, card, cards))
      else:
        cattach[card] = cards
        cards.target(False)
        notify("{} equips {} to {}.".format(me, card, cards))
  else:
    whisper("Incorrect targets, select only 1 target.")

#---------------------------------------------------------------------------
# Marker functions
#---------------------------------------------------------------------------

def addMarker(cards, x = 0, y = 0, marker = None, quantity = 0):
    mute()
    if marker == None:
      marker, quantity = askMarker()
    if quantity == 0: return
    for c in cards:
        c.markers[marker] += quantity
        notify("{} adds {} {} counters to {}.".format(me, quantity, marker[0], c))

#---------------------------
# Movement actions
#---------------------------
	
def destroy(card, x = 0, y = 0):
	mute()
	src = card.group
	fromText = " from the table" if src == table else " from their " + src.name
	card.moveTo(shared.piles['Discards'])
	notify("{} destroys {}{}.".format(me, card, fromText))

def discard(card, x = 0, y = 0):
    mute()
    src = card.group
    fromText = " from the table" if src == table else " from their " + src.name
    card.moveTo(shared.piles['Discards'])
    notify("{} discards {}{}.".format(me, card, fromText))

def toDeck(card, x = 0, y = 0):
    mute()
    src = card.group
    fromText = " from the table" if src == table else " from their " + src.name
    card.moveTo(shared.piles['Main Deck'])
    notify("{} returns {} to the deck{}.".format(me, card, fromText))

def toHand(card, x = 0, y = 0):
    mute()
    src = card.group
    fromText = " from the table" if src == table else " from their " + src.name
    card.moveTo(me.hand)
    notify("{} returns {} to their hand{}.".format(me, card.name, fromText))

#---------------------------------------------------------------------------
# Hand actions
#---------------------------------------------------------------------------
	
def play(card, x = 0, y = 0):
   mute()
   src = card.group
   placeCard(card)
   notify("{} plays {} from their {}.".format(me, card, src.name))

def randomDiscard(group):
   mute()
   card = group.random()
   if card == None: return
   card.moveTo(shared.piles['Discards'])
   notify("{} randomly discards {}.".format(me, card))

#---------------------------------------------------------------------------
# Piles actions
#---------------------------------------------------------------------------
def shuffle(group, x = 0, y = 0):
    group.shuffle()

def randomPick(group):
    mute()
    card = group.random()
    if card == None: return
    notify("{} randomly picks {} from the {}.".format(me, card, group))

def draw(group, x = 0, y = 0):
    if len(group) == 0: return
    mute()
    group[0].moveTo(me.hand)
    notify("{} draws a card.".format(me))

def drawMany(group, count = None):
    if len(group) == 0: return
    mute()
    if count == None: count = askInteger("Draw how many cards?", 5)
    for c in group.top(count): c.moveTo(me.hand)
    notify("{} draws {} cards.".format(me, count))

def mill(group = shared.piles['Main Deck'], count = None):
    if len(group) == 0: return
    mute()
    if count == None: count = askInteger("Mill how many cards?", 1)
    for c in group.top(count): c.moveTo(shared.piles['Discards'])
    notify("{} mills the top {} cards from the Deck.".format(me, count))

def shuffleIntoDeck(group = shared.piles['Discards']):
    mute()
    Deck = shared.piles['Main Deck']
    for c in group: c.moveTo(Deck)
    Deck.shuffle()
    notify("{} shuffles the {} into the Deck.".format(me, group.name))

def revealTopDeck(group, x = 0, y = 0):
    mute()
    if group[0].isFaceUp:
        notify("{} hides {} from the top of the Deck.".format(me, group[0]))
        group[0].isFaceUp = False
    else:
        group[0].isFaceUp = True
        notify("{} reveals {} from the top of the Deck.".format(me, group[0]))
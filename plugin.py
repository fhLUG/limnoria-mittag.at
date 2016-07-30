###
# Copyright (c) 2016, fhLUG
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import json
import re

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Mittag')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

POWERED_BY = u'(powered by mittag.at)'

class Mittag(callbacks.Plugin):
    """
    Fetches the current meal list for hagenberg from mittag.at,
    optionally filtered by a user-provided search string
    """
    threaded = True

    def hunger(self, irc, msg, args, search):
        """
        Get lunch menus. Usage: hunger [<search>]
        """
        prefixNick = self.registryValue('prefixNick')
        apiKey = self.registryValue('apiKey')
        coord = self._makeCoord()
        distance = self.registryValue('distance')

        menus = _filter(
            _restaurants(
                _nearest(
                    _retrieve(apiKey, coord),
                    distance)),
            search)

        if not menus:
            irc.reply(
                u'Nix zu essen heute. ' + POWERED_BY,
                prefixNick=prefixNick,
                sendImmediately=True)
        else:
            for menu in menus:
                irc.reply(
                    menu,
                    prefixNick=prefixNick,
                    sendImmediately=True)

            irc.reply(
                POWERED_BY,
                prefixNick=prefixNick,
                sendImmediately=True)

    def _makeCoord(self):
        """
        Creates a coord dict with values from config
        :return: a new coordinate dict
        """
        return {
                'latitude': self.registryValue('latitude'),
                'longitude': self.registryValue('longitude')
                }

    hunger = wrap(hunger, [optional('text')])

def _retrieve(apikey, coord):
    """
    Downloads the the json of the mittag API (v1.2.3)
    :param apikey: key for the mittag api
    :param coord: longitude and latitude of the position
    :return: a json array of menus
    """

    lat = str(coord['latitude'])
    lon = str(coord['longitude'])

    r = urllib2.urlopen("http://www.mittag.at/api/1/menus?"
                                "lat=" + lat + "&lon=" + lon +
                                "&apikey=" + apikey + "&v=1.2.3")
    arr = json.loads(r.read().decode())['menus']  # Take only the children
    r.close()
    return arr


def _nearest(menus, threshold):
    """
    Filters the json based on the distance and if the distance is greater than
    the threshold, the restaurant will be removed from the json
    :param menus: response from the API as objects
    :param threshold: limit of distance
    :return: a filtered json
    """
    return [menu for menu in menus if float(menu['distance']) < float(threshold)]


def _restaurants(menus):
    """
    Cleans up menu strings
    :param menus: menus to clean up
    :return: list containing cleaned up menu strings
    """
    return [_string(menu) for menu in menus]


def _string(menu):
    """
    Converts a menu dict to a single string. Strips empty lines, new lines,
    carriage returns, and allergen labels
    :param menu: dict containing 'restaurantName' and 'menu'
    :return: string in the form of "restaurant name: menu"
    """
    line = _normalizeNewlines(u"%s: %s" % (menu['restaurantName'], menu['menu']))

    line = _removeAllergenInformation(line)

    # collapse whitespace
    return re.sub(r'\s+', u' ', line)

def _filter(menus, search = ''):
    """
    Filters menus based on a search term.
    Search is case insensitive.
    :param menus: menus to filter
    :param search: optional search term
    :return: filterered menus
    """
    if not search:
        return menus

    return [menu
            for menu
            in menus
            if re.search(re.escape(search), menu, re.IGNORECASE)]

def _normalizeNewlines(menuitem):
    """
    Normalizes newlines and replaces them with single
    spaces or '|' to discern different menus.
    :param menuitem: menu item to normalize
    :return: the normalized menu item
    """
    return menuitem\
        .replace(u"\r\n", u"\n") \
        .replace(u"\n\n", u" | ") \
	.replace(u"\n", u" ")

def _removeAllergenInformation(line):
    """
    Removes EU food allergen labels.
    :param line: line to remove allergen labels from
    :return: line without allergen labels
    """
    return re.sub(r'\s?\([A-HL-PR,\s]+\)', u'', line)

Class = Mittag

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

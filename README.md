Mittag
======

Mittag is a plugin for the popular Supybot/Limnoria IRC bot.
It provides access to the http://mittag.at API via IRC commands.

Currently, only German messages are supported.

Commands
--------

Currently only two commands are supported:

* `!hunger`: list all available menus of today
* `!hunger <filter>`: list today's menus which contain the given substring

In action
---------

    08:38 < knittl> !hunger campina
    08:38 < fhtux> Campina: Tagessuppe | Cordon Bleu vom Schwein mit Reis und Kartoffel | Hirse Mozzarellalaibchen auf Ofengemüse mit Kräuterdip | Dessert
    08:38 < fhtux> (powered by mittag.at)

Installation
------------

Install like any other Supybot/Limnoria plugin, by copying to the appropriate location.

Configuration
-------------

You only have to update the config file with your API key and GPS coordinates.
All config options can be found under the `supybot.plugins.Mittag` key.
Config options can be set globally or per channel.

* `apiKey`: Your API key required by the mittag.at API.
* `latitude`/`longitude`: Coordinate used to query lunch menus.
* `distance`: Maximum distance to center location for menus to be included.

License
-------

This work is licensed under the 3-clause BSD license.
For more details consult the LICENSE file.

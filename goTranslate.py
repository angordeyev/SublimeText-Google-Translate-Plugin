# -*- coding: utf-8 -*-
# author:mtimer
# https://github.com/MTimer/SublimeText-Google-Translate-Plugin

import sublime
import sublime_plugin
import json
from pprint import pprint
if sublime.version() < '3':
    from core.translate import *
else:
    from .core.translate import *

settings = sublime.load_settings("goTranslate.sublime-settings")

class GoTranslateCommand(sublime_plugin.TextCommand):

    def run(self, edit, proxy_enable = settings.get("proxy_enable"), proxy_type = settings.get("proxy_type"), proxy_host = settings.get("proxy_host"), proxy_port = settings.get("proxy_port"), source_language = settings.get("source_language"), target_language = settings.get("target_language")):
        if not source_language:
            source_language = settings.get("source_language")
        if not target_language:
            target_language = settings.get("target_language")
        if not proxy_enable:
            proxy_enable = settings.get("proxy_enable")
        if not proxy_type:
            proxy_type = settings.get("proxy_type")
        if not proxy_host:
            proxy_host = settings.get("proxy_host")
        if not proxy_port:
            proxy_port = settings.get("proxy_port")
        target_type = settings.get("target_type")

        for region in self.view.sel():
            v = self.view
            whole_line = False
            if not region.empty():
                selection = v.substr(region)
                coordinates = v.sel()
            else:
                selection = v.substr(v.line(v.sel()[0]))
                coordinates = v.line(v.sel()[0])
                whole_line = True

            if selection:
                print('selection(' + selection + ')' )
                largo = len(selection)
                print('')
                print('largo long(' + str(largo) + ')' )

                if largo > 256:
                    print('')
                    print('ERR: line too long to translate and it will fail, consider spliting it, shorting it, making two or more.')
                    print('')
                    return

                selection = selection.encode('utf-8')

                translate = GoogleTranslate(proxy_enable, proxy_type, proxy_host, proxy_port, source_language, target_language)

                if not target_language:
                    self.view.run_command("go_translate_to")
                    return
                else:
                    result = translate.translate(selection, target_type)

                print('edit')
                pprint(edit)

                print('coordinates')
                pprint(coordinates)

                print('result')
                pprint(result)

                if not whole_line:
                    v.replace(edit, region, result)
                else:
                    v.replace(edit, coordinates, result)

                if not source_language:
                    detected = 'Auto'
                else:
                    detected = source_language
                sublime.status_message(u'Done! (translate '+detected+' --> '+target_language+')')
            else:
                print('nothing to translate')
                print('selection(' + selection + ')' )

    def is_visible(self):
        for region in self.view.sel():
            if not region.empty():
                return True
        return False

class GoTranslateInfoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("goTranslate.sublime-settings")
        source_language = settings.get("source_language")
        target_language = settings.get("target_language")
        proxy_enable = settings.get("proxy_enable")
        proxy_type = settings.get("proxy_type")
        proxy_host = settings.get("proxy_host")
        proxy_port = settings.get("proxy_port")

        v = self.view
        selection = v.substr(v.sel()[0])

        translate = GoogleTranslate(proxy_enable, proxy_type, proxy_host, proxy_port, source_language, target_language)

        text = (json.dumps(translate.langs, ensure_ascii = False, indent = 2))

        v.replace(edit, v.sel()[0], text)

class GoTranslateToCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("goTranslate.sublime-settings")
        source_language = settings.get("source_language")
        target_language = settings.get("target_language")
        proxy_enable = settings.get("proxy_enable")
        proxy_type = settings.get("proxy_type")
        proxy_host = settings.get("proxy_host")
        proxy_port = settings.get("proxy_port")

        v = self.view
        selection = v.substr(v.sel()[0])

        translate = GoogleTranslate(proxy_enable, proxy_type, proxy_host, proxy_port, source_language, target_language)

        text = (json.dumps(translate.langs['langs'], ensure_ascii = False))
        continents = json.loads(text)
        lkey = []
        ltrasl = []

        for (slug, title) in continents.items():
            lkey.append(slug)
            ltrasl.append(title+' ['+slug+']')

        def on_done(index):
            if index >= 0:
                self.view.run_command("go_translate", {"target_language": lkey[index]})

        self.view.window().show_quick_panel(ltrasl, on_done)

    def is_visible(self):
        for region in self.view.sel():
            if not region.empty():
                return True
        return False


def plugin_loaded():
    global settings
    settings = sublime.load_settings("goTranslate.sublime-settings")
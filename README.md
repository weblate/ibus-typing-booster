# Ibus-typing-booster

Faster typing by context sensitive completion.

## Introduction

Ibus-typing-booster is a completion input method to speedup typing.

The project was started in 2010 for Fedora 15. The original purpose was to make typing of
Indic languages easier and faster by providing completion and spell checking suggestions.

Originally it was forked from ibus-table whose developer was Yu Yuwei acevery@gmail.com,
with contributions from Caius “kaio” Chance me@kaio.net.

Since then ibus-typing-booster has been improved to support many other languages as well
(most languages except Chinese and Japanese are supported).

Recently the capapility to type different languages at the same time without having to
switch between languages has been added.

## Developers:
  
  - Mike FABIAN mfabian@redhat.com
  - Anish Patil anish.developer@gmail.com

## Features
  
  - Context sensitive completions.
  - Learns from user input.
  - Can be trained by supplying files containing typical user input.
  - If available, hunspell and hunspell dictionaries will also be used to provide not only
    completion but also spellchecking suggestions (But ibus-typing-booster works also
    without hunspell by learning only from user input).
  - Can be used with any keyboard layout.
  - Almost all input methods supplied by libm17n are supported (including the inscript2
    input methods).
  - Several input methods and languages can be used at the same time without switching.
  - Predicts Unicode symbols and emoji as well.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Online documentation

[ibus-typing-booster home page on github](http://mike-fabian.github.io/ibus-typing-booster/)

[ibus-typing-booster documentation page](http://mike-fabian.github.io/ibus-typing-booster/documentation.html)

## Default key and mouse bindings

[Default key bindings](http://mike-fabian.github.io/ibus-typing-booster/documentation.html#key-bindings)

[Default mouse bindings](http://mike-fabian.github.io/ibus-typing-booster/documentation.html#mouse-bindings)

A copy of these bindings is included below in this readme for convenience.

## Bug reports

You can report bugs here:

[ibus-typing-booster issue tracker on github](https://github.com/mike-fabian/ibus-typing-booster/issues)

## Contributing translations

The best (easiest) way to contribute translations is using this
[online translation platform](https://translate.stg.fedoraproject.org/projects/ibus-typing-booster/).

## Development

If  you want to build from  source or contribute to the development, see the
[ibus-typing-booster development page](http://mike-fabian.github.io/ibus-typing-booster/development.html).

There  you should also find the requirements for building from source
for most systems.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A copy of the default key bindings and mouse bindings documentation is
included here for convenience:

## Table of default key bindings

Some of these key bindings can be customized in the setup tool.
The following table explains the defaults:

```
┏━━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Key combination  │                         Effect                          ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Commit the preëdit (or the selected candidate, if any)  ┃
┃ Space             │ and send a space to the application, i.e. commit the    ┃
┃                   │ typed string followed by a space.                       ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ Return            │ Commit the preëdit (or the selected candidate, if any)  ┃
┃                   │ and send a Return to the application.                   ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ Enter             │ Commit the preëdit (or the selected candidate, if any)  ┃
┃                   │ and send a Enter to the application.                    ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Bound by default to the commands                        ┃
┃                   │ “select_next_candidate” and “enable_lookup”.            ┃
┃                   │                                                         ┃
┃                   │   • If the option “☐ Enable suggestions by Tab key” is  ┃
┃                   │     not set: “Tab” always just executes                 ┃
┃                   │     “select_next_candidate” which selects the next      ┃
┃                   │     candidate from the candidate list.                  ┃
┃                   │   • If the option “☑ Enable suggestions by Tab key” is  ┃
┃                   │     set, no candidate list is shown by default:         ┃
┃ Tab               │       □ If no candidate list is shown: “enable_lookup”  ┃
┃                   │         is executed which requests to show the          ┃
┃                   │         candidate list (nothing might be shown if no    ┃
┃                   │         candidates can be found).                       ┃
┃                   │       □ If a candidate list is already shown:           ┃
┃                   │         “select_next_candidate” is executed which       ┃
┃                   │         selects the next candidate in the list. After   ┃
┃                   │         each commit and after each change of the        ┃
┃                   │         contents of the preëdit, the candidate list     ┃
┃                   │         will be hidden again until the “enable_lookup”  ┃
┃                   │         requests it again.                              ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Bound by default to the command                         ┃
┃ Shift+Tab         │ “select_previous_candidate”.                            ┃
┃                   │ Selects the previous candidate in the candidate list.   ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Bound by default to the command “cancel”.               ┃
┃                   │                                                         ┃
┃                   │   • When a candidate is selected (no matter whether     ┃
┃                   │     this is a normal lookup table or a “related” lookup ┃
┃                   │     table): Show the first page of that lookup table    ┃
┃                   │     again with no candidate selected.                   ┃
┃ Escape            │   • When no candidate is selected:                      ┃
┃                   │       □ When a lookup table with related candidates is  ┃
┃                   │         shown or a lookup table where upper/lower-case  ┃
┃                   │         has been changed by typing the Shift key is     ┃
┃                   │         shown: go back to the original lookup table.    ┃
┃                   │       □ When a normal lookup table is shown: close it   ┃
┃                   │         and clear the preëdit.                          ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Move cursor one typed key left in the preëdit text. May ┃
┃ Left (Arrow left) │ trigger a commit if the left end of the preëdit is      ┃
┃                   │ reached.                                                ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Move cursor to the left end of the preëdit text. If the ┃
┃ Control+Left      │ cursor is already at the left end of the preëdit text,  ┃
┃                   │ trigger a commit and send a Control+Left to the         ┃
┃                   │ application.                                            ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ Right (Arrow      │ Move cursor one typed key right in preëdit text. May    ┃
┃ right)            │ trigger a commit if the right end of the preëdit is     ┃
┃                   │ reached.                                                ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Move cursor to the right end of the preëdit text. If    ┃
┃ Control+Right     │ the cursor is already at the right end of the preëdit   ┃
┃                   │ text, trigger a commit and send a Control+Right to the  ┃
┃                   │ application.                                            ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ Backspace         │ Remove the typed key to the left of the cursor in the   ┃
┃                   │ preëdit text.                                           ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ Control+Backspace │ Remove everything to the left of the cursor in the      ┃
┃                   │ preëdit text.                                           ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ Delete            │ Remove the typed key to the right of the cursor in the  ┃
┃                   │ preëdit text.                                           ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ Control+Delete    │ Remove everything to the right of the cursor in the     ┃
┃                   │ preëdit text.                                           ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Bound by default to the command                         ┃
┃ Down (Arrow down) │ “select_next_candidate”.                                ┃
┃                   │ Selects the next candidate.                             ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Bound by default to the command                         ┃
┃ Up (Arrow up)     │ “select_previous_candidate”.                            ┃
┃                   │ Selects the previous candidate.                         ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ Page_Up           │ Bound by default to the command “lookup_table_page_up”. ┃
┃                   │ Shows the previous page of candidates.                  ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Bound by default to the command                         ┃
┃ Page_Down         │ “lookup_table_page_down”.                               ┃
┃                   │ Shows the next page of candidates.                      ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ F1                │ Commit the candidate with the label “1” followed by a   ┃
┃                   │ space                                                   ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ F2                │ Commit the candidate with the label “2” followed by a   ┃
┃                   │ space                                                   ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ ...               │ ...                                                     ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ F9                │ Commit the candidate with the label “9” followed by a   ┃
┃                   │ space                                                   ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Remove the candidate with the label “1” from the        ┃
┃ Control+F1        │ database of learned user input (If possible, if this    ┃
┃                   │ candidate is not learned from user input, nothing       ┃
┃                   │ happens).                                               ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Remove the candidate with the label “2” from the        ┃
┃ Control+F2        │ database of learned user input (If possible, if this    ┃
┃                   │ candidate is not learned from user input, nothing       ┃
┃                   │ happens).                                               ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ …                 │ …                                                       ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Remove the candidate with the label “9” from the        ┃
┃ Control+F9        │ database of learned user input (If possible, if this    ┃
┃                   │ candidate is not learned from user input, nothing       ┃
┃                   │ happens).                                               ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Same as F1 … F9 if the option “Use digits as select     ┃
┃                   │ keys” is enabled. Enabling that option makes selecting  ┃
┃                   │ candidates a bit easier because the number keys 1 … 9   ┃
┃                   │ are closer to the fingers then F1 … F9 on most          ┃
┃                   │ keyboards. On the other hand, it makes completing when  ┃
┃ 1 … 9             │ typing numbers impossible and it makes typing strings   ┃
┃                   │ which are combinations of letters and numbers like “A4” ┃
┃                   │ more difficult. If digits are used as select keys,      ┃
┃                   │ numbers can only be typed when no candidate list is     ┃
┃                   │ shown. In most cases this means that numbers can only   ┃
┃                   │ be typed when nothing else has been typed yet and the   ┃
┃                   │ preëdit is empty.                                       ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ Control+1 …       │ Same as Control+F1 … Control+F9 if the option “Use      ┃
┃ Control+9         │ digits as select keys” is enabled.                      ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Bound by default to the command                         ┃
┃                   │ “toggle_emoji_prediction”.                              ┃
┃ AltGr+F6          │ Toggle the emoji and Unicode symbol prediction on/off.  ┃
┃                   │ This has the same result as using the setup tool to     ┃
┃                   │ change this.                                            ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Bound by default to the command                         ┃
┃                   │ “toggle_off_the_record”.                                ┃
┃                   │ Toggle the “Off the record” mode. This has the same     ┃
┃                   │ result as using the setup tool to change this.          ┃
┃                   │ While “Off the record” mode is on, learning from user   ┃
┃ AltGr+F9          │ input is disabled. If learned user input is available,  ┃
┃                   │ predictions are usually much better than predictions    ┃
┃                   │ using only dictionaries. Therefore, one should use this ┃
┃                   │ option sparingly. Only if one wants to avoid saving     ┃
┃                   │ secret user input to disk it might make sense to use    ┃
┃                   │ this option temporarily.                                ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ AltGr+F10         │ Bound by default to the command “setup”.                ┃
┃                   │ Opens the setup tool.                                   ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃                   │ Bound by default to the command “lookup_related”.       ┃
┃ AltGr+F12         │ Shows related emoji and Unicode symbols or related      ┃
┃                   │ words                                                   ┃
┠───────────────────┼─────────────────────────────────────────────────────────┨
┃ AltGr+Space       │ Insert a literal space into the preëdit.                ┃
┗━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

When more than one input method at the same time is used, the following
additional key bindings are available:

```
┏━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃     Key      │                            Effect                            ┃
┃ combination  │                                                              ┃
┠──────────────┼──────────────────────────────────────────────────────────────┨
┃              │ Bound by default to the command “next_input_method”.         ┃
┃ Control+Down │ Switches the input method used for the preëdit to the next   ┃
┃              │ input method.                                                ┃
┠──────────────┼──────────────────────────────────────────────────────────────┨
┃              │ Bound by default to the command “previous_input_method”.     ┃
┃ Control+Up   │ Switches the input method used for the preëdit to the        ┃
┃              │ previous input method.                                       ┃
┗━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```


## Mouse bindings

These mouse bindings are currently hardcoded and can not yet be customized.

```
┏━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   Mouse event    │                          Effect                          ┃
┠──────────────────┼──────────────────────────────────────────────────────────┨
┃ Button 1 click   │ Commit the candidate clicked on followed by a space      ┃
┃ on a candidate   │ (Same as F1…F9).                                         ┃
┠──────────────────┼──────────────────────────────────────────────────────────┨
┃ Control + Button │ Remove clicked candidate from database of learned user   ┃
┃ 1 click on a     │ input (If possible, if this candidate is not learned     ┃
┃ candidate        │ from user input, nothing happens).                       ┃
┠──────────────────┼──────────────────────────────────────────────────────────┨
┃ Button 3 click   │ Show related emoji and Unicode symbols or related words  ┃
┃ on a candidate   │ (Same as AltGr+F12).                                     ┃
┠──────────────────┼──────────────────────────────────────────────────────────┨
┃ Control + Button │ Toggle the emoji and Unicode symbol prediction on/off    ┃
┃ 3 click anywhere │ (Same as AltGr+F6). This has the same result as using    ┃
┃ in the candidate │ the setup tool to change this.                           ┃
┃ list             │                                                          ┃
┠──────────────────┼──────────────────────────────────────────────────────────┨
┃                  │ Toggle the “Off the record” mode (Same as AltGr+F9).     ┃
┃                  │ This has the same result as using the setup tool to      ┃
┃                  │ change this.                                             ┃
┃ Alt + Button 3   │ While “Off the record” mode is on, learning from user    ┃
┃ click anywhere   │ input is disabled. If learned user input is available,   ┃
┃ in the candidate │ predictions are usually much better than predictions     ┃
┃ list             │ using only dictionaries. Therefore, one should use this  ┃
┃                  │ option sparingly. Only if one wants to avoid saving      ┃
┃                  │ secret user input to disk it might make sense to use     ┃
┃                  │ this option temporarily.                                 ┃
┗━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

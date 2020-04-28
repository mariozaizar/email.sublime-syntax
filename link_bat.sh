#!/bin/bash

# We use bat to verify the sintax. bat is a cat clone with syntax highlighting
# and Git integration. bat uses syntect library for syntax highlighting which
# can read any .sublime-syntax file and theme.
#
# https://github.com/sharkdp/bat

bat --version || brew install bat # Mac OS only

BAT_PATH=$(bat --config-dir)

mkdir -p "$BAT_PATH/syntaxes"
mkdir -p "$BAT_PATH/themes"

INSTALL_PATH=${BAT_PATH}/syntaxes
ln -siv "$PWD/email.sublime-syntax" "$INSTALL_PATH"

bat cache --build
bat --list-languages | grep "Email"

bat demo/email.eml

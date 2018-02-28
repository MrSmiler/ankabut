#!/bin/bash

pyuic5 -x ../../ui_files/mainwindow_ui.ui -o mainwindow_ui.py
pyuic5 -x ../../ui_files/ask_download_ui.ui -o ask_download_ui.py
pyuic5 -x ../../ui_files/download_progress_ui.ui -o download_progress_ui.py
pyuic5 -x ../../ui_files/download_finished_ui.ui -o download_finished_ui.py
pyuic5 -x ../../ui_files/add_link_ui.ui -o add_link_ui.py
pyuic5 -x ../../ui_files/settings_ui.ui -o settings_ui.py

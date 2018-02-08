#!/bin/bash

pyuic5 -x mainwindow_ui.ui -o mainwindow_ui.py
pyuic5 -x ask_download_ui.ui -o ask_download_ui.py
pyuic5 -x download_progress_ui.ui -o download_progress_ui.py
pyuic5 -x download_finished_ui.ui -o download_finished_ui.py
pyuic5 -x add_link_ui.ui -o add_link_ui.py
pyuic5 -x settings_ui.ui -o settings_ui.py

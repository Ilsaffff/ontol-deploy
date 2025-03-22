import streamlit as st
import subprocess
import shutil
import os
import uuid
from zipfile import ZipFile

DEFAULT_TEXT = """version: '1.0'
title: ''
author: ''
description: ''

types:
...

functions:
...

hierarchy:
...

"""

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())
    st.session_state['first_load'] = True


def create_zip(directory):
    zip_filename = os.path.join(directory, 'results.zip')
    with ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file == 'results.zip':
                    continue
                arcname = os.path.relpath(file_path, directory)
                zipf.write(file_path, arcname)
    return zip_filename


def rm_dir(dir: str):
    if os.path.exists(dir):
        shutil.rmtree(dir)


USER_RESULTS_DIR = f'results/{st.session_state["session_id"]}'
ZIP_FILE = f'{USER_RESULTS_DIR}.zip'


def generate_image(dsl_text):
    os.makedirs(USER_RESULTS_DIR, exist_ok=True)
    input_file = os.path.join(USER_RESULTS_DIR, 'ontology.ontol')

    with open(input_file, 'w') as f:
        f.write(dsl_text)

    subprocess.run(['ontol', input_file, '--output-dir', USER_RESULTS_DIR], check=True)
    create_zip(USER_RESULTS_DIR)


if st.session_state['first_load']:
    st.session_state['first_load'] = False

st.title('Генерация PNG с помощью Ontol')

dsl_code = st.text_area('Введите DSL-код', value=DEFAULT_TEXT, height=800)

if st.button('Сгенерировать изображение', icon='🖼'):
    if dsl_code.strip():
        try:
            generate_image(dsl_code)
            image_path = os.path.join(USER_RESULTS_DIR, 'ontology.png')
            st.image(image_path, caption='Сгенерированное изображение')
        except Exception as e:
            st.error(f'Ошибка генерации: {e}')
    else:
        st.warning('Введите код на DSL Ontol')

zip_path = os.path.join(USER_RESULTS_DIR, 'results.zip')
if os.path.exists(zip_path):
    with open(zip_path, 'rb') as f:
        st.download_button(
            '📥 Скачать ZIP', f, file_name='results.zip', mime='application/zip'
        )
    rm_dir(USER_RESULTS_DIR)

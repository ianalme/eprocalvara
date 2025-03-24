import os

def delete_files_in_tempfiles(folder_path):
    # Navega pelos itens na pasta especificada
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # Verifica se o item é um arquivo e não o próprio script Python
        if os.path.isfile(item_path) and not item_path.endswith('.py'):
            os.remove(item_path)
        # Se for uma pasta, chama a função recursivamente
        elif os.path.isdir(item_path):
            delete_files_in_tempfiles(item_path)

# Caminho para a pasta 'tempfiles'
tempfiles_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# Chama a função para deletar arquivos
delete_files_in_tempfiles(tempfiles_directory)

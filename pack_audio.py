import struct
import os
import wave

RSC_TABLEINFO_SIZE = 8
RSC_TABLEENTRY_SIZE = 8


# Substtui as faixas no RES

def update_audio_in_res(input_res_file, audio_files, is_be=False):
    # Abrir o arquivo .res para leitura e escrita
    with open(input_res_file, 'r+b') as input_file:
        input_file_size = os.path.getsize(input_res_file)
        print(f'Original Filesize: {input_file_size}')

        # Ler a tabela de registros
        input_file.seek(-RSC_TABLEINFO_SIZE, os.SEEK_END)
        if is_be:
            res_table_offset, res_table_count = struct.unpack('>II', input_file.read(RSC_TABLEINFO_SIZE))
        else:
            res_table_offset, res_table_count = struct.unpack('<II', input_file.read(RSC_TABLEINFO_SIZE))

        print(f'Table offset: {res_table_offset}\nNumber of records: {res_table_count}')

        if res_table_offset != input_file_size - RSC_TABLEINFO_SIZE - RSC_TABLEENTRY_SIZE * res_table_count:
            raise ValueError("Something's wrong with your resource file")

        input_file.seek(res_table_offset)
        records_info = []

        # Ler a tabela de registros
        for _ in range(res_table_count):
            if is_be:
                offset, size = struct.unpack('>II', input_file.read(RSC_TABLEENTRY_SIZE))
            else:
                offset, size = struct.unpack('<II', input_file.read(RSC_TABLEENTRY_SIZE))
            records_info.append((offset, size))

        # Atualizar os dados dos registros com os novos áudios
        for i, (offset, size) in enumerate(records_info):
            audio_file_path = audio_files.get(i, None)

            if audio_file_path and os.path.exists(audio_file_path):
                with wave.open(audio_file_path, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())

                    # Verificar se o tamanho é o mesmo do original
                    #if len(frames) != size:
                        #raise ValueError(f"File {audio_file_path} size does not match the original")

                    # Substituir os dados no arquivo .res
                    input_file.seek(offset)
                    input_file.write(frames)
            else:
                print(f"Audio file for record {i} not found or does not exist: {audio_file_path}")

        print('Update complete!')


# Caminho do arquivo .res original e arquivos de áudio para substituir
input_res_file = 'C:/Users/jrcn0/Downloads/scummvm-tools-2.7.0-win32-x86_64/VOICESS.RES'
audio_files = {
    0: 'C:/Users/jrcn0/Downloads/scummvm-tools-2.7.0-win32-x86_64/audio_output/0.wav',
    1: 'C:/Users/jrcn0/Downloads/scummvm-tools-2.7.0-win32-x86_64/audio_output/1.wav',
    2: 'C:/Users/jrcn0/Downloads/scummvm-tools-2.7.0-win32-x86_64/audio_output/2.wav'
}
is_be = False  # Defina como True se o arquivo usar big-endian

# Chama a função para atualizar os áudios
update_audio_in_res(input_res_file, audio_files, is_be)

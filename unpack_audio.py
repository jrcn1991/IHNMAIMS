import struct
import os
import wave

RSC_TABLEINFO_SIZE = 8
RSC_TABLEENTRY_SIZE = 8

# Extraia s faxias no RES
class Record:
    def __init__(self, offset, size):
        self.offset = offset
        self.size = size


def unpack(input_name, out_dir_name, is_be=False):
    with open(input_name, 'rb') as input_file:
        input_file_size = os.path.getsize(input_name)
        print(f'Filesize: {input_file_size}')

        input_file.seek(-RSC_TABLEINFO_SIZE, os.SEEK_END)

        if is_be:
            res_table_offset, res_table_count = struct.unpack('>II', input_file.read(RSC_TABLEINFO_SIZE))
        else:
            res_table_offset, res_table_count = struct.unpack('<II', input_file.read(RSC_TABLEINFO_SIZE))

        print(f'Table offset: {res_table_offset}\nnumber of records: {res_table_count}')

        if res_table_offset != input_file_size - RSC_TABLEINFO_SIZE - RSC_TABLEENTRY_SIZE * res_table_count:
            raise ValueError("Something's wrong with your resource file")

        input_file.seek(res_table_offset)

        input_table = []

        for _ in range(res_table_count):
            if is_be:
                offset, size = struct.unpack('>II', input_file.read(RSC_TABLEENTRY_SIZE))
            else:
                offset, size = struct.unpack('<II', input_file.read(RSC_TABLEENTRY_SIZE))

            print(f'Record: {_}, offset: {offset}, size: {size}')

            if offset > input_file_size or offset + size > input_file_size:
                raise ValueError("The offset points outside the file")

            input_table.append(Record(offset, size))

        # Salvar a tabela de registros e os dados extraídos
        records_info = []
        sample_rate = 44100
        num_channels = 1
        sample_width = 2

        for i, record in enumerate(input_table):
            output_file_path = os.path.join(out_dir_name, f'{i}.wav')

            with open(output_file_path, 'wb') as output_file:
                input_file.seek(record.offset)
                buf = input_file.read(record.size)

                if len(buf) % sample_width != 0:
                    raise ValueError("O tamanho dos dados não é múltiplo da largura da amostra")

                with wave.open(output_file_path, 'wb') as wav_file:
                    wav_file.setnchannels(num_channels)
                    wav_file.setsampwidth(sample_width)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(buf)

            # Adicionar informações de registro para reconstrução
            records_info.append((record.offset, record.size))

        # Salvar a tabela de registros em um arquivo separado
        with open(os.path.join(out_dir_name, 'records_info.bin'), 'wb') as info_file:
            for offset, size in records_info:
                if is_be:
                    info_file.write(struct.pack('>II', offset, size))
                else:
                    info_file.write(struct.pack('<II', offset, size))

        print('Done!')


# Caminho do arquivo de entrada e diretório de saída definidos diretamente no código
input_file = 'C:/Users/jrcn0/Downloads/scummvm-tools-2.7.0-win32-x86_64/VOICESS.RES'
output_dir = 'C:/Users/jrcn0/Downloads/scummvm-tools-2.7.0-win32-x86_64/audio_output'
is_be = False  # Defina como True se o arquivo usar big-endian

# Cria o diretório de saída, se não existir
os.makedirs(output_dir, exist_ok=True)

# Chama a função de desempacotamento
unpack(input_file, output_dir, is_be)



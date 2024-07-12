import csv
import multiprocessing
from tqdm import tqdm
from Blockthon import Wallet, Bitcoin
from mnemonic import Mnemonic

# Função para gerar endereços Bitcoin e chaves privadas a partir de mnemônicos
def generate_wallet_info(mnemonics):
    seed_bytes = Wallet.Mnemonic_To_Bytes(mnemonics)
    privatekey = Wallet.Bytes_To_PrivateKey(seed_bytes)
    
    p2pkhAddress = Bitcoin.Address_From_PrivateKey(privatekey, Type='P2PKH')
    p2shAddress = Bitcoin.Address_From_PrivateKey(privatekey, Type='P2SH')
    p2wpkhAddress = Bitcoin.Address_From_PrivateKey(privatekey, Type='P2WPKH')
    p2wshAddress = Bitcoin.Address_From_PrivateKey(privatekey, Type='P2WSH')
    p2wpkhSegwit = Bitcoin.Address_From_PrivateKey(privatekey, Type='P2WPKHinP2SH')
    p2wshSegwit = Bitcoin.Address_From_PrivateKey(privatekey, Type='P2WSHinP2SH')
    
    return {
        "PrivateKey": privatekey,
        "P2PKH": p2pkhAddress,
        "P2SH": p2shAddress,
        "P2WPKH": p2wpkhAddress,
        "P2WSH": p2wshAddress,
        "P2WPKHinP2SH": p2wpkhSegwit,
        "P2WSHinP2SH": p2wshSegwit
    }

# Lista de línguas
languages = [
    "english", "chinese_simplified", "chinese_traditional", "french",
    "italian", "japanese", "korean", "spanish", "turkish", "czech", "portuguese"
]

# Função para gerar as informações e escrever no arquivo CSV
def generate_and_write_csv(filename, mnemonics_length, total_entries):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Language', f'Mnemonic ({mnemonics_length} words)', 'PrivateKey', 'Bitcoin P2PKH', 'Bitcoin P2SH', 
                        'Bitcoin P2WPKH', 'Bitcoin P2WSH', 'Bitcoin P2WPKH in Segwit', 'Bitcoin P2WSH in Segwit'])

        entries_written = 0
        with tqdm(total=total_entries, desc=f'{mnemonics_length}-word mnemonics') as pbar:
            for language in languages:
                mnemo = Mnemonic(language)
                while entries_written < total_entries:
                    mnemonics = mnemo.generate(mnemonics_length)
                    wallet_info = generate_wallet_info(mnemonics)
                    writer.writerow([language,
                                     mnemonics,
                                     wallet_info["PrivateKey"],
                                     wallet_info["P2PKH"],
                                     wallet_info["P2SH"],
                                     wallet_info["P2WPKH"],
                                     wallet_info["P2WSH"],
                                     wallet_info["P2WPKHinP2SH"],
                                     wallet_info["P2WSHinP2SH"]])
                    entries_written += 1
                    pbar.update(1)

                    # Verificar se atingiu o número total de entradas desejadas
                    if entries_written >= total_entries:
                        break

        print(f"Foram geradas {entries_written} entradas de carteira para mnemônicos de {mnemonics_length} palavras.")

# Função para executar a geração e escrita em multiprocessamento
def generate_and_write_csv_multiprocess(total_entries_per_type):
    processes = []
    pool = multiprocessing.Pool(processes=3)  # Utilizando 3 processos para os três tipos de mnemônicos

    # Gerar arquivos CSV para cada tipo de mnemônico em processos diferentes
    pool.apply_async(generate_and_write_csv, args=('wallet_info_12.csv', 128, total_entries_per_type))
    pool.apply_async(generate_and_write_csv, args=('wallet_info_18.csv', 192, total_entries_per_type))
    pool.apply_async(generate_and_write_csv, args=('wallet_info_24.csv', 256, total_entries_per_type))

    pool.close()
    pool.join()

# Perguntar ao usuário quantas informações ele deseja
total_entries_per_type = int(input("Quantas informações de carteira deseja gerar para cada tipo de mnemônico (12, 18 e 24 palavras)? "))

# Executar a geração e escrita em multiprocessamento
generate_and_write_csv_multiprocess(total_entries_per_type)

print("Processo concluído.")

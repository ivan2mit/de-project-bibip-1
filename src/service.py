db_path = 'src/db/'+'models'+'.db'
with open(db_path, "r+") as f: # r+ нужен для того, чтобы была возможность писать в тот же файл, что читаем.
    strings = f.read().split('\n')
    print(strings)

    f.seek(0)
    for string in strings:
        f.write(string+(500-len(string))*' '+'\n')



    

import config

import os, re, binascii, hashlib

input_files = []
input_contents = {}

def check_sum(word):
    sum = 0
    for c in word:
        sum += int(binascii.b2a_hex(c), 16)
    return sum


def generate_n_gram(word_array, n):
    assert n > 0
    grams = []
    if len(word_array) < n:
        return [word_array]
    for i in range(0, len(word_array) - n):
        tmp = []
        for j in range(0, n):
            tmp.append(word_array[i + j])
        grams.append(' '.join(tmp))
    return grams


def finger_print(word_array):
    sums = []
    grams = generate_n_gram(word_array, config.gram_size)
    for sentence in grams:
        checkSum = check_sum(sentence)
        if checkSum % config.hash_mode == 0:
            sums.append(check_sum(sentence))
    sums.sort()
    return sums


def rabin(word, n):
    if n == 128:
        return int(hashlib.md5(word).hexdigest(), 16)
    else:
        pass # TODO


def simhash(word_array):
    word_weights = {}
    for word in word_array:
        if word_weights.has_key(word):
            word_weights[word] += 1
        else:
            word_weights[word] = 1
    fingerprint = ''
    for i in range(0, config.simhash_fingerprint_size):
        val = 0
        for word in word_weights:
            rb = rabin(word, config.simhash_fingerprint_size)
            if (rb / (2 ** (config.simhash_fingerprint_size - i - 1))) % 2 != 0:
                val += word_weights[word]
            else:
                val -= word_weights[word]
        if val > 0:
            fingerprint += '1'
        else:
            fingerprint += '0'
    return fingerprint


def preprocess():
    regex = re.compile(r'\w{1,}')
    input_files = map(lambda file: file[0:-4], os.listdir(config.input_folder_path))
    for file_name in input_files:
        f = open(config.input_folder_path + '/' + file_name + '.txt', 'r')
        content = f.read()
        tmp = filter(lambda word: len(word) > 0, regex.findall(content))
        input_contents[file_name] = tmp


def exact_detect():
    check_sums = {}
    for file in input_contents:
        content = input_contents[file]
        sum = 0
        for word in content:
            sum += check_sum(word)
        if not check_sums.has_key(sum):
            check_sums[sum] = [file]
        else:
            check_sums[sum].append(file)

    f = open(config.exact_output_file_path, 'w')
    for sum in check_sums:
        if len(check_sums[sum]) > 1:
            for i in range(0, len(check_sums[sum]) - 1):
                for j in range(i + 1, len(check_sums[sum])):
                    f.write(check_sums[sum][i] + '-' + check_sums[sum][j] + '\n')
    f.close()
    print 'exact detect done.'


def near_detect():
    files = []
    file_fingerprints = []
    for file in input_contents:
        files.append(file)
        content = input_contents[file]
        fingerprint = simhash(content)
        file_fingerprints.append(fingerprint)
    l = len(file_fingerprints)
    assert l > 1
    f = open(config.near_output_file_path, 'w')
    for i in range(0, l - 1):
        for j in range(i + 1, l):
            f1 = file_fingerprints[i]
            f2 = file_fingerprints[j]
            near_size = 0
            for k in range(0, config.simhash_fingerprint_size):
                if f1[k] == f2[k]:
                    near_size += 1
            if float(near_size) / config.simhash_fingerprint_size >= 0.9:
                # near duplicates
                f.write(files[i] + '-' + files[j] + '\n')
    f.close()
    print 'near detect done.'


def finn_detect():
    pass


def main():
    preprocess()
    exact_detect()
    near_detect()
    finn_detect()

if __name__ == '__main__':
    main()

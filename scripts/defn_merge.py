#!/usr/bin/python3

# Read a file of definitions and a lemma file, and merge them, index on the lemmas.
# Preserve any rank and pronounciation column entries. no need to keep other columns.
# Cope with bad data where possible


def parse_definition_line(number, line, definitions, purposes):
    """break up a line into the parts:
        "word"	"Definition"	"is-a"	"Japanese" """
    # print("parse_definition_line:", number, line, definitions, purposes)
    tokens = line.split('\t')
    howmany = len(tokens)
    if howmany != 4:
        print("line", number, ": incorrect number of tokens:", howmany, ", should be 4", tokens)
        return number+1
    key = tokens[0]
    # print("key:",key)
    definition = tokens[1]
    # print("definition:",definition)
    purpose = tokens[2]
    # print("purpose:",purpose)
    definitions[key] = definition
    purposes[key] = purpose
    return number + 1


def test04():
    """Can we parse the file used in test01? It has specific contents. """
    # "Meanings"	"English Definition"	"POS"	"J Translation"
    contents = handle_file("ten_liner")
    if contents is not None:
        defs = {}
        funs = {}
        linecount = 0
        for line in contents:
            linecount = parse_definition_line(linecount, line, defs, funs)
        if 10 == linecount:
            if '"Meanings"' in defs:
                if '"English Definition"' == defs.get('"Meanings"'):
                    if '"adj"' == funs.get('"able"'):
                        print("test04 pass")
                    else:
                        print("test04 fail funs(able)=", funs.get('"able"'))
                else:
                    print("test04 fail Meanings defs:", defs)
            else:
                print("test04 fail defs:", defs)
        else:
            print("test04 fail linecount:", linecount)
    else:
        print("test04 fail")
    return


def test03():
    """Can we parse the keyword, definition and function out of a line?"""
    line = "keyword\tdefinition\tfunction\t能力"
    defs = {}
    funs = {}
    parse_definition_line(1, line, defs, funs)
    if 'keyword' in defs:
        if 'definition' == defs.get('keyword'):
            if 'keyword' in funs:
                if 'function' == funs.get('keyword'):
                    print("test03 pass")
                else:
                    print("test03 fail funs:", funs)
            else:
                print("test03 fail funs:", funs)
        else:
            print("test03 fail defs:", defs)
    else:
        print("test03 fail")
    return


def handle_file(name):
    """open the file and read it"""
    if name is not None:
        try:
            reader = open(name, 'r')
            lines = reader.readlines()
            reader.close()
            return lines
        except IOError:
            print("Trouble reading", name, "file.")
            return
    else:
        print("handle_file for", name, "is None")
    return


def test02():
    """Can we cope with a missing file?"""
    count = handle_file("mia")
    if count is None:
        print("test02 pass")
    else:
        print("test02 fail count:", count)
    return


def test01():
    """Can we read the test dictionary file? """
    count = handle_file("ten_liner")
    if count is not None:
        if 10 == len(count):
            print("test01 pass")
            return
        else:
            print("test01 fail as count is", len(count))
    else:
        print("test01 fail as count is None")
    return


def test11():
    """Can we read the test SFI file? """
    count = handle_file("ten_sfi")
    if count is not None:
        if 10 == len(count):
            print("test11 pass")
            return
        else:
            print("test11 fail as count is", len(count))
    else:
        print("test11 fail as count is None")
    return


def parse_sfi_line(number, line, lemmas, pronounces):
    """break up a line into the parts. There should be 12 tokens"""
    # print("parse_sfi_line:", number, line)
    tokens = line.split('\t')
    howmany = len(tokens)
    if howmany != 12:
        print("line", number, ": incorrect number of tokens:", howmany, ", should be 12")
        return number+1
    lemma = tokens[0]
    if lemma == '':
        print("line", number, "missing a lemma. Skipping:", line)
        return number+1
    # print("line:", number, "lemma:",lemma)
    pronounce = tokens[1]
    # definition = tokens[2]
    # wordlist = tokens[3]
    rank = tokens[4]
    # at the end of the list, the rank is no longer listed.
    if '.' in str(rank):
        print("line", number, "lemma:", lemma, "rank:", rank, "has a dot")
        return number+1
    # print("rank:",rank)
    # sfi = float(tokens[5])
    # print("sfi:",sfi)
    # U_fpermil = tokens[6]
    # D_ivide = tokens[7]
    # frequency = tokens[8]
    # subrank = tokens[9]
    # coverage = tokens[10]
    # cummulative = tokens[11]
    # print("cummulative:",cummulative)
    # print("line:", number, "lemma:",lemma, "pronounce:", pronounce, "rank:", rank)
    lemmas[lemma] = rank
    if pronounce != '':
        pronounces[lemma] = pronounce
    return number + 1


def test12():
    """Can we parse the lemma, and rank out of a file?"""
    contents = handle_file("ten_sfi")
    lemmas = {}
    proz = {}
    linecount = 0
    for line in contents:
        linecount = parse_sfi_line(linecount, line, lemmas, proz)
    print("lemmas:", lemmas)
    if '"and"' in lemmas:
        if '3' == lemmas.get('"and"'):
            print("test12 pass")
        else:
            print("test12 fail lemmas:", lemmas)
    else:
        print("test12 fail, can't find and")
    return


def test_words():
    """ Unit test driver """
    test01()
    test02()
    test03()
    test04()
    test11()
    test12()


def merge_words(definition_file, sfi_file, debuglimit):
    """ Open both definition and sfi lemma file and merge them."""
    word_contents = handle_file(definition_file)
    word_definitions = {}
    word_purposes = {}
    word_count = 0
    for word_line in word_contents:
        word_count = parse_definition_line(word_count, word_line, word_definitions, word_purposes)
    lemma_contents = handle_file(sfi_file)
    lemma_words = {}
    lemma_proz = {}
    lemma_count = 0
    for lemma_line in lemma_contents:
        lemma_count = parse_sfi_line(lemma_count, lemma_line, lemma_words, lemma_proz)

    print("word_count:", word_count, "lemma_count:", lemma_count)

    for word in lemma_words.keys():
        if debuglimit > 0:
            say = str(lemma_words.get(word))
            say += "\t"
            say += word
            say += "\t"
            proz = lemma_proz.get(word)
            if proz is not None:
                say += proz
            say += "\t"
            defn = word_definitions.get(word)
            if defn is not None:
                say += defn
            say += "\t"
            print(say)
            debuglimit -= 1
        else:
            break
    return


if __name__ == "__main__":
    # test_words()
    # merge_words("ten_liner", "ten_sfi")
    # merge_words("E-J+Definitions+from+NGSL+Builder.csv", "ten_sfi")
    merge_words("E-J+Definitions+from+NGSL+Builder.csv", "NGSL+SFI.csv", 3810)

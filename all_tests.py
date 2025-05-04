from regex_fsm import RegexFSM

regex_pattern1 = "a[^bc]d*e"
regex_compiler1 = RegexFSM(regex_pattern1)
assert regex_compiler1.check_string("afde") is True
assert regex_compiler1.check_string("azzzze") is False
assert regex_compiler1.check_string("abde") is False      
assert regex_compiler1.check_string("acde") is False
assert regex_compiler1.check_string("agde") is True
assert regex_compiler1.check_string("agggge") is False

regex_pattern2 = ".[aeiou]+z?"
regex_compiler2 = RegexFSM(regex_pattern2)
assert regex_compiler2.check_string("baeiou") is True
assert regex_compiler2.check_string("zaeiouz") is True
assert regex_compiler2.check_string("b") is False

regex_pattern3 = "[x-z]?a[0-9]*b+"
regex_compiler3 = RegexFSM(regex_pattern3)
assert regex_compiler3.check_string("xa123b") is True
assert regex_compiler3.check_string("a99bbb") is True
assert regex_compiler3.check_string("a") is False

regex_pattern4 = ".?q+r+"
regex_compiler4 = RegexFSM(regex_pattern4)
assert regex_compiler4.check_string("qqrrr") is True
assert regex_compiler4.check_string("qqr") is True
assert regex_compiler4.check_string("r") is False

regex_pattern5 = "[a-m][^aeiou][x-z]*"
regex_compiler5 = RegexFSM(regex_pattern5)
assert regex_compiler5.check_string("bpy") is True
assert regex_compiler5.check_string("mbzzz") is True
assert regex_compiler5.check_string("aju") is False

regex_pattern6 = "m*n?o+p?"
regex_compiler6 = RegexFSM(regex_pattern6)
assert regex_compiler6.check_string("mmnooo") is True
assert regex_compiler6.check_string("noop") is True
assert regex_compiler6.check_string("o") is True
assert regex_compiler6.check_string("m") is False

regex_pattern7 = "a.*b+c?"
regex_compiler7 = RegexFSM(regex_pattern7)
assert regex_compiler7.check_string("axxxbbb") is True
assert regex_compiler7.check_string("ab") is True
assert regex_compiler7.check_string("a123") is False

regex_pattern8 = "[^a-z]+END"
regex_compiler8 = RegexFSM(regex_pattern8)
assert regex_compiler8.check_string("123END") is True
assert regex_compiler8.check_string("!@#END") is True
assert regex_compiler8.check_string("abcEND") is False

regex_pattern9 = ".+[A-Z]?[0-9]*"
regex_compiler9 = RegexFSM(regex_pattern9)
assert regex_compiler9.check_string("helloA123") is True
assert regex_compiler9.check_string("!9") is True
assert regex_compiler9.check_string("") is False

regex_pattern10 = ".[^x-z]+[a-c]*"
regex_compiler10 = RegexFSM(regex_pattern10)
assert regex_compiler10.check_string("1qaa") is True
assert regex_compiler10.check_string("zyaa") is False
assert regex_compiler10.check_string("!mbbb") is True
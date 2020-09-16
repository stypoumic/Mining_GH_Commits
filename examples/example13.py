from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	
	code_before ="""public static void main(String[] args){
                      for (int c = a ^ b; c != 0; c = c >> 1) {
                          int a=1;
                          int b=10;
                          System.out.println(c);
                      }
                    }"""
	code_after = """public static void main(String[] args){
                      for (int c = a ^ b; c != 0; c = c >>> 1) {
                          int a = -1;
                          int b=10;
                          System.out.println(c);
                      }
                    }"""

	results = cmatcher.search(code_before = code_before, code_after = code_after, score_by = {'code_additions': True, 'code_deletions': True})

	for result in results[:10]:
		print("Score %.3f Message: %s" %(result[-1], result[0]))


# Expected output:
"""
Score 1.000 Message: 5.06 Changed from arithmetic to logical shift to handle negative numbers
Score 0.514 Message: Allow negative offsets (except special value -1) when getting a field value with sun.misc.Unsafe
Score 0.514 Message: Fix file size always 0 bug when downloading file
Score 0.514 Message: Fix MediaUtils.shuffle

Was ignoring the first element of the list
Score 0.345 Message: JLANG-47 Ensure the binary format can be converted into the text format
Score 0.300 Message: Add demo processing engine
Score 0.300 Message: TCK: Request -1 in 309 instead of a random non-positive number
Score 0.300 Message: TCK: Request -1 in 309 instead of a random non-positive number
Score 0.214 Message: Revert "Replace check for `is target` with 'is not 0'"

This reverts commit ce6bbbda182a59bae21e5f97ee67d0eb6d4c217
Score 0.214 Message: Transactions per second / rollbacks per second view fixed
"""
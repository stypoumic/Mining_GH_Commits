from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	
	code_before = """public int sum(int[] ar){
					    int s = 0;
					    for (int i=0; i < ar.length; i++){
					        s += ar[i];
					    }
					    return s;
					}"""
	code_after = """public int sum(int[] ar){
					    int s = 0;
					    for (int elem : ar){
					        s += elem;
					    }
					    return s;
					}"""

	results = cmatcher.search(code_before = code_before, code_after = code_after, score_by = {'code_additions': True, 'code_deletions': True})

	for result in results[:10]:
		print("Score %.3f Message: %s" %(result[-1], result[0]))

# Expected output:
"""
Score 0.466 Message: Replaced for(int..) with new Java 5 for each
Score 0.442 Message: Convert for into foreach
Score 0.410 Message: Add null check on passphrase before clearing
Score 0.396 Message: Replace `for` loop with `foreach`
Score 0.374 Message: Fix StackArray.java resize()
Score 0.330 Message: for each loop
Score 0.329 Message: P10: Simplified Java solution
Score 0.323 Message: consistent use of foreach loop
Score 0.310 Message: Reversed the order in which empty slots are chosen so that it prefers the lower left again
Score 0.307 Message: Bugfix: The loop requesting the garbage collection in cleanup() was running almost infinitely
"""

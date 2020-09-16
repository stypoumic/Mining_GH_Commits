from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	
	code_before = """public int sum(List<Integer> list){
					    int s = 0;
					    for (int i=0; i < list.size(); i++){
					        int l = list.get(i);
				            s += l;
					    }
					    return s;
					}"""
	code_after = """public int sum(List<Integer> list){
					    int s = 0;
					    for (int i=0; i < list.size(); i++){
					        int l = list.get(i);
					        if (l != null)
					            s += l;
					    }
					    return s;
					}"""

	results = cmatcher.search(code_before = code_before, code_after = code_after, score_by = {'code_additions': True, 'code_deletions': True})

	for result in results[:10]:
		print("Score %.3f Message: %s" %(result[-1], result[0]))

# Expected output:
"""
Score 0.417 Message: Center to the first known gps location
Score 0.366 Message: Fix npe when input object field has a wrong name
Score 0.346 Message: Fix NPE on using invalid uiLines
Score 0.341 Message: Set progress to NULL_PROGRESS_CALLBACK if callback is null
Score 0.337 Message: - fixed updating view in ViewTaskFragment
Score 0.337 Message: fixed DynamicLongArray expandCapacity
Score 0.337 Message: Update currently play song variable on UI thread\nThis ensures the variable is always read and assigned\non the UI thread preventing any issues when the song\nis changing right as it is clicked
Score 0.337 Message: lastResponse was always overwritten to null value---now corrected\ngit-svn-id: https://rest-client.googlecode.com/svn/trunk@733 08545216-953f-0410-99bf-93b34cd2520f
Score 0.323 Message: Fixed bug where activity is lost while photo is being downloaded
Score 0.322 Message: Possible fix for gh 354
"""

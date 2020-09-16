from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	
	code_before = """public String getFull(List<String> list){
					    StringBuffer sb = new StringBuffer();  
					    for (int i=0; i < list.size(); i++){
					        sb.append(text(list.get(i)));
					    }
					    return sb.toString();
					}"""
	code_after = """public String getFull(List<String> list){
					    StringBuilder sb = new StringBuilder();  
					    for (int i=0; i < list.size(); i++){
					        sb.append(text(list.get(i)));
					    }
					    return sb.toString();
					}"""

	results = cmatcher.search(code_before = code_before, code_after = code_after, score_by = {'code_additions': True, 'code_deletions': True})

	for result in results[:10]:
		print("Score %.3f Message: %s" %(result[-1], result[0]))

# Expected output:
"""
Score 1.000 Message: Changed to StringBuilder for performance
Score 0.889 Message: StringBuffer => StringBuilder, thanks IntelliJ ^_^
Score 0.889 Message: modify source read
Score 0.889 Message: Use StringBuilder to build the menu path string
Score 0.889 Message: Use StringBuilder instead of StringBuffer, no thread-safeness required here
Score 0.883 Message: Use StringBuilder instead of StringBuffer
Score 0.865 Message: replace obsolete StringBuffer by StringBuilder
Score 0.741 Message: No jira, replaced StringBuffer with StringBuilder.\n\ngit-svn-id: https://svn.apache.org/repos/asf/incubator/opennlp/trunk@1199649 13f79535-47bb-0310-9956-ffa450edef68
Score 0.653 Message: Accidentally checked in a StringBuffer instead of Builder
Score 0.645 Message: Performance issue when building strings \n\nImprove performance by using StringBuilder instead of StringBuffer
"""
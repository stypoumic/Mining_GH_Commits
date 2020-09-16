from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	
	code_before = """void Restart() { 
                        stateOwner.addStateListener(new StateChangeListener() {
                        
                            public void onStateChange(State oldState, State newState) {
                                // do something with the old and new state.
                            }
                        });
                     }"""
	code_after = """void Restart() { 
                        stateOwner.addStateListener(
                            (oldState, newState) -> System.out.println("State changed")
                    );
                    }"""

	results = cmatcher.search(code_before = code_before, code_after = code_after, score_by = {'code_additions': True, 'code_deletions': True})

	for result in results[:10]:
		print("Score %.3f Message: %s" %(result[-1], result[0]))


# Expected output:
"""
Score 0.261 Message: Service starting converted to Lambda
Score 0.258 Message: Service polling refactored to lambda
Score 0.198 Message: Added config:get/set environment confiration tool tweaks
Score 0.186 Message: Add a trace indicating when the verticles are deployed
Score 0.185 Message: Fixed print output
Score 0.182 Message: Added some feedback to echoserver (when started)
Score 0.174 Message: Added info to benchmark.

git-svn-id: http://encog-java.googlecode.com/svn/trunk/encog-examples@3566 f90f6e9a-ac51-0410-b353-d1b83c6f6923
Score 0.174 Message: System.out only in debug mode for GhIssueTest to cleanup mvn test
results
Score 0.174 Message: Adding some debugging statements
Score 0.174 Message: put back logging for the index error
"""
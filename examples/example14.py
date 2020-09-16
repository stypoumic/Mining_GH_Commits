from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	
	code_before ="""@Override public boolean equals(Object obj){
                      final Model other=(Model)obj;
                      return this.mId != null && (this.mTableInfo.getTableName() == other.mTableInfo.getTableName()) && (this.mId == other.mId);
                    }"""
	code_after = """@Override public boolean equals(Object obj){
                      final Model other=(Model)obj;
                      return this.mId != null && (this.mTableInfo.getTableName().equals(other.mTableInfo.getTableName())) && (this.mId.equals(other.mId));
                    }"""

	results = cmatcher.search(code_before = code_before, code_after = code_after, score_by = {'code_additions': True, 'code_deletions': True})

	for result in results[:10]:
		print("Score %.3f Message: %s" %(result[-1], result[0]))


# Expected output:
"""
Score 1.000 Message: Fixed Model `equals` method

`equals` was comparing the memory address of the object members, rather than the values. Changed to use `equals` methods instead of `==`
Score 1.000 Message: Fixed Model `equals` method

`equals` was comparing the memory address of the object members, rather than the values. Changed to use `equals` methods instead of `==`
Score 0.398 Message: Model.equals() checks for id==null now
Score 0.398 Message: Model.equals() checks for id==null now
Score 0.368 Message: Fix compare of two Integer values to use equals instead of ==
Score 0.324 Message: Do not announce when tracker list is empty
Score 0.322 Message: make Tuple.compareTo() method compare scores

Make Tuple.compareTo() method to not violate contract on case when scores are equal
Score 0.309 Message: Include diagnostic request frequency in equality comparison
Score 0.298 Message: Bugfix: dump-rdf wouldn't work with custom base URI and serialization format other than RDF/XML(-ABBREV)
Score 0.296 Message: Changing the sameTrack method slightly
"""        

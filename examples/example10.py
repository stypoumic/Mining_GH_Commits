from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	
	code_before ="""private InputStream getStream(){
                      return stream;
                    }"""
	code_after = """protected InputStream getStream(){
                      return stream;
                    }"""

	results = cmatcher.search(code_before = code_before, code_after = code_after, score_by = {'code_additions': True, 'code_deletions': True})

	for result in results[:10]:
		print("Score %.3f Message: %s" %(result[-1], result[0]))


# Expected output:
"""
Score 1.000 Message: 暴露createFlutterView，供在flutterView add 原生view
Score 1.000 Message: expose self() to subclass
Score 1.000 Message: changed "getFiles" to protected
Score 1.000 Message: changed constructor visibility from private to protected in order to be able to derive from Application
Score 1.000 Message: Allow InstanceWebClient to be extended
Score 1.000 Message: Make API extendable
Score 1.000 Message: make getStream protected in Response
Score 1.000 Message: Make getColor protected in DefaultClusterRenderer
Score 1.000 Message: configuration method should be protected so that we can override the configuration
Score 1.000 Message: Make getClassLoader0() protected


git-svn-id: http://anonsvn.jboss.org/repos/javassist/trunk@314 30ef5769-5b8d-40dd-aea6-55b5d6557bb3
"""
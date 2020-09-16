from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	results = cmatcher.search(message = "illegal argument exception", score_by={'message': True})

	first_result = results[0]

	print("\n\nMessage: " + str(first_result[0]))
	print("\n\nCode Before:\n" + str(first_result[1]))
	print("\n\nCode After:\n" + str(first_result[2]))
	print("\n\nCode Deletions:\n" + str(first_result[3]))
	print("\n\nCode Additions:\n" + str(first_result[4]))
    
    
# Expected output:
"""

Message: illegal global id should yield illegal argument exception


Code Before:
public ResolvedGlobalId fromGlobalId(String globalId){
  String[] split=Base64.fromBase64(globalId).split(":",2);
  return new ResolvedGlobalId(split[0],split[1]);
}


Code After:
public ResolvedGlobalId fromGlobalId(String globalId){
  String[] split=Base64.fromBase64(globalId).split(":",2);
  if (split.length != 2) {
    throw new IllegalArgumentException(String.format("expecting a valid global id, got %s",globalId));
  }
  return new ResolvedGlobalId(split[0],split[1]);
}


Code Deletions:



Code Additions:
        if (split.length != 2) {
            throw new IllegalArgumentException(String.format("expecting a valid global id, got %s", globalId));
        }
"""
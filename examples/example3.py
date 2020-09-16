from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	results = cmatcher.search(message = "number format exception", score_by={'message': True})

	first_result = results[0]

	print("\n\nMessage: " + str(first_result[0]))
	print("\n\nCode Before:\n" + str(first_result[1]))
	print("\n\nCode After:\n" + str(first_result[2]))
	print("\n\nCode Deletions:\n" + str(first_result[3]))
	print("\n\nCode Additions:\n" + str(first_result[4]))

# Expected output:
"""

Message: fixed number format


Code Before:
@Override public String format(double amount){
  if (amount == 1) {
    return String.format("%f %s",amount,getMoneyNameSingular());
  }
 else {
    return String.format("%f %s",amount,getMoneyNamePlural());
  }
}


Code After:
@Override public String format(double amount){
  amount=Math.ceil(amount);
  if (amount == 1) {
    return String.format("%d %s",(int)amount,getMoneyNameSingular());
  }
 else {
    return String.format("%d %s",(int)amount,getMoneyNamePlural());
  }
}


Code Deletions:
            return String.format("%f %s", amount, getMoneyNameSingular());
            return String.format("%f %s", amount, getMoneyNamePlural());


Code Additions:
        amount = Math.ceil(amount);
            return String.format("%d %s", (int)amount, getMoneyNameSingular());
            return String.format("%d %s", (int)amount, getMoneyNamePlural());

"""

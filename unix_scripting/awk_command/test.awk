BEGIN{
  st="ggs this is a string."
  }

{
  
  print(index($st "s"))
  }

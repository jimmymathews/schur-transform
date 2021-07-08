for i in [2..6] do
tbl:=CharacterTable("symmetric", i);
Print("Character table GAP output magic header separator\n");
Print("Begin section: Rank of symmetric group\n");
Print(String(i));
Print("\nEnd section.\n");
Print("Begin section: Character function values\n");
PrintObj(Irr(tbl));
Print("\nEnd section.\n");
Print("Begin section: Partition labels for the sequence of character functions\n");
PrintObj(CharacterParameters(tbl));
Print("\nEnd section.\n");
Print("Begin section: Partition labels for the sequence of conjugacy classes (the domain of each character function)\n");
PrintObj(ClassParameters(tbl));
Print("\nEnd section.\n");
Print("Begin section: Sizes of conjugacy classes\n");
PrintObj(SizesConjugacyClasses(tbl));
Print("\nEnd section.\n");
od;

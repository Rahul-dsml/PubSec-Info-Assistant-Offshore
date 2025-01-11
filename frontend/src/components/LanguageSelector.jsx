import React, { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { ArrowDown, ArrowDownNarrowWide, Globe } from "lucide-react";

export default function LanguageDropdown({language,setLanguage}) {
 

  const handleLanguageChange = (selectedLanguage) => {
    setLanguage(selectedLanguage);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          className=" bg-slate-700 hover:border-slate-400 hover:border rounded-full hover:bg-slate-800 transition-all ease-in"
          
        >
          <Globe className="" />
          <span className="">{language}</span>
          <ArrowDown />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-fit bg-slate-700 text-white outline-cyan-500 border-cyan-500">
        <DropdownMenuLabel>Select Language</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => handleLanguageChange("English")}>
          English
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleLanguageChange("Arabic")}>
          Arabic
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

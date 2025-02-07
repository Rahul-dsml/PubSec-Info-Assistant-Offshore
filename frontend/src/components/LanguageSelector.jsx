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
import i18n from "@/i18n";

export default function LanguageDropdown({ language, setLanguage }) {
  const handleLanguageChange = (selectedLanguage) => {
    setLanguage(selectedLanguage.lang);
    i18n.changeLanguage(selectedLanguage?.code);
  };

  const languages = [
    { code: "en", lang: "English" },
    { code: "ar", lang: "العربية" },
  ];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button className=" bg-slate-700 hover:border-slate-400 hover:border rounded-full hover:bg-slate-800 transition-all ease-in">
          <Globe className="" />
          <span className="">{language}</span>
          <ArrowDown />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-fit bg-slate-700 text-white outline-cyan-500 border-cyan-500">
        <DropdownMenuLabel>Select Language</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {languages.map((language, index) => {
          return (
            <DropdownMenuItem
              key={index}
              onClick={() => handleLanguageChange(language)}
            >
              {language.lang}
            </DropdownMenuItem>
          );
        })}
        {/* <DropdownMenuItem onClick={() => handleLanguageChange("English")}>
          English
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleLanguageChange("Arabic")}>
          Arabic
        </DropdownMenuItem> */}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}


// ── apt_cobaltstrike.yar ──
/*
   LICENSE
   Copyright (C) 2015 JPCERT Coordination Center. All Rights Reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following acknowledgments and disclaimers.
   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following acknowledgments and disclaimers
      in the documentation and/or other materials provided with the distribution.
   3. Products derived from this software may not include "JPCERT Coordination
      Center" in the name of such derived product, nor shall "JPCERT
      Coordination Center"  be used to endorse or promote products derived
      from this software without prior written permission. For written
      permission, please contact pr@jpcert.or.jp.

   ACKNOWLEDGMENTS AND DISCLAIMERS
   Copyright (C) 2015 JPCERT Coordination Center

   This software is based upon work funded and supported by the Ministry of
   Economy, Trade and Industry.

   Any opinions, findings and conclusions or recommendations expressed in this
   software are those of the author(s) and do not necessarily reflect the views
   of the Ministry of Economy, Trade and Industry.

   NO WARRANTY. THIS JPCERT COORDINATION CENTER SOFTWARE IS FURNISHED ON
   AN "AS-IS" BASIS. JPCERT COORDINATION CENTER MAKES NO WARRANTIES OF
   ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT
   NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY,
   EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE SOFTWARE. JPCERT
   COORDINATION CENTER DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH
   RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.

   This software has been approved for public release and unlimited distribution.
*/

rule APT_CobaltStrike_Beacon_Indicator {
   meta:
      description = "Detects CobaltStrike beacons"
      author = "JPCERT"
      reference = "https://github.com/JPCERTCC/aa-tools/blob/master/cobaltstrikescan.py"
      date = "2018-11-09"
      id = "8508c7a0-0131-59b1-b537-a6d1c6cb2b35"
   strings:
      $v1 = { 73 70 72 6E 67 00 }
      $v2 = { 69 69 69 69 69 69 69 69 }
   condition:
      uint16(0) == 0x5a4d and filesize < 300KB and all of them
}

rule HKTL_CobaltStrike_Beacon_Strings {
   meta:
      author = "Elastic"
      description = "Identifies strings used in Cobalt Strike Beacon DLL"
      reference = "https://www.elastic.co/blog/detecting-cobalt-strike-with-memory-signatures"
      date = "2021-03-16"
      id = "af558aa2-a3dc-5a7a-bc74-42bb2246091c"
   strings:
      $s1 = "%02d/%02d/%02d %02d:%02d:%02d"
      $s2 = "Started service %s on %s"
      $s3 = "%s as %s\\%s: %d"
   condition:
      2 of them
}

rule HKTL_CobaltStrike_Beacon_XOR_Strings {
   meta:
      author = "Elastic"
      description = "Identifies XOR'd strings used in Cobalt Strike Beacon DLL"
      reference = "https://www.elastic.co/blog/detecting-cobalt-strike-with-memory-signatures"
      date = "2021-03-16"
      /* Used for beacon config decoding in THOR */
      xor_s1 = "%02d/%02d/%02d %02d:%02d:%02d"
      xor_s2 = "Started service %s on %s"
      xor_s3 = "%s as %s\\%s: %d"
      id = "359160a8-cf1c-58a8-bf7f-c09a8d661308"
   strings:
      $s1 = "%02d/%02d/%02d %02d:%02d:%02d" xor(0x01-0xff)
      $s2 = "Started service %s on %s" xor(0x01-0xff)
      $s3 = "%s as %s\\%s: %d" xor(0x01-0xff)

      $fp1 = "MalwareRemovalTool"
   condition:
      2 of ($s*) and not 1 of ($fp*)
}

rule HKTL_CobaltStrike_Beacon_4_2_Decrypt {
   meta:
      author = "Elastic"
      description = "Identifies deobfuscation routine used in Cobalt Strike Beacon DLL version 4.2"
      reference = "https://www.elastic.co/blog/detecting-cobalt-strike-with-memory-signatures"
      date = "2021-03-16"
      id = "63b71eef-0af5-5765-b957-ccdc9dde053b"
   strings:
      $a_x64 = {4C 8B 53 08 45 8B 0A 45 8B 5A 04 4D 8D 52 08 45 85 C9 75 05 45 85 DB 74 33 45 3B CB 73 E6 49 8B F9 4C 8B 03}
      $a_x86 = {8B 46 04 8B 08 8B 50 04 83 C0 08 89 55 08 89 45 0C 85 C9 75 04 85 D2 74 23 3B CA 73 E6 8B 06 8D 3C 08 33 D2}
   condition:
      any of them
}

rule HKTL_Win_CobaltStrike : Commodity {
   meta:
      author = "threatintel@volexity.com"
      date = "2021-05-25"
      description = "The CobaltStrike malware family."
      hash = "b041efb8ba2a88a3d172f480efa098d72eef13e42af6aa5fb838e6ccab500a7c"
      reference = "https://www.volexity.com/blog/2021/05/27/suspected-apt29-operation-launches-election-fraud-themed-phishing-campaigns/"
      id = "113ba304-261f-5c59-bc56-57515c239b6d"
   strings:
      $s1 = "%s (admin)" fullword
      $s2 = {48 54 54 50 2F 31 2E 31 20 32 30 30 20 4F 4B 0D 0A 43 6F 6E 74 65 6E 74 2D 54 79 70 65 3A 20 61 70 70 6C 69 63 61 74 69 6F 6E 2F 6F 63 74 65 74 2D 73 74 72 65 61 6D 0D 0A 43 6F 6E 74 65 6E 74 2D 4C 65 6E 67 74 68 3A 20 25 64 0D 0A 0D 0A 00}
      $s3 = "%02d/%02d/%02d %02d:%02d:%02d" fullword
      $s4 = "%s as %s\\%s: %d" fullword
      $s5 = "%s&%s=%s" fullword
      $s6 = "rijndael" fullword
      $s7 = "(null)"
   condition:
      all of them
}


// ── example.yar ──
/*
   Example YARA Rule — Placeholder
   Add your custom .yar rule files to this directory.
*/

rule ExampleMalwareSignature {
    meta:
        description = "Example placeholder rule"
        author = "MemForensics Framework"
        date = "2026-05-02"

    strings:
        $suspicious_string = "This is a placeholder"

    condition:
        $suspicious_string
}


// ── gen_mimikatz.yar ──
import "pe"

/* Mimikatz */

rule Mimikatz_Memory_Rule_1 : APT {
   meta:
      author = "Florian Roth"
      date = "2014-12-22"
      modified = "2023-07-04"
      score = 70
      nodeepdive = 1
      description = "Detects password dumper mimikatz in memory (False Positives: an service that could have copied a Mimikatz executable, AV signatures)"
      id = "55cc7129-5ea0-5545-a8f6-b5306a014dd0"
   strings:
      $s1 = "sekurlsa::wdigest" fullword ascii
      $s2 = "sekurlsa::logonPasswords" fullword ascii
      $s3 = "sekurlsa::minidump" fullword ascii
      $s4 = "sekurlsa::credman" fullword ascii

      $fp1 = "\"x_mitre_version\": " ascii
      $fp2 = "{\"type\":\"bundle\","
      $fp3 = "use strict" ascii fullword
      $fp4 = "\"url\":\"https://attack.mitre.org/" ascii
   condition:
      1 of ($s*) and not 1 of ($fp*)
}

/* we have much better rules now
rule Mimikatz_Memory_Rule_2 : APT {
   meta:
      description = "Mimikatz Rule generated from a memory dump"
      author = "Florian Roth (Nextron Systems) - Florian Roth"
      score = 75
      date = "2014-12-22"
      modified = "2023-05-19"
      reference = "https://blog.gentilkiwi.com/mimikatz"
   strings:
      $s0 = "sekurlsa::" ascii
      $x1 = "cryptprimitives.pdb" ascii
      $x2 = "Now is t1O" ascii fullword
      $x4 = "ALICE123" ascii
      $x5 = "BOBBY456" ascii
   condition:
      $s0 and 1 of ($x*)
}
*/

rule mimikatz : FILE {
   meta:
      description      = "mimikatz"
      author         = "Benjamin DELPY (gentilkiwi)"
      tool_author      = "Benjamin DELPY (gentilkiwi)"
      modified = "2022-11-16"
      id = "840a5b8c-a311-50bc-a099-6b8ab1492e12"
   strings:
      $exe_x86_1      = { 89 71 04 89 [0-3] 30 8d 04 bd }
      $exe_x86_2      = { 8b 4d e? 8b 45 f4 89 75 e? 89 01 85 ff 74 }

      $exe_x64_1      = { 33 ff 4? 89 37 4? 8b f3 45 85 c? 74}
      $exe_x64_2      = { 4c 8b df 49 [0-3] c1 e3 04 48 [0-3] 8b cb 4c 03 [0-3] d8 }

/*
      $dll_1         = { c7 0? 00 00 01 00 [4-14] c7 0? 01 00 00 00 }
      $dll_2         = { c7 0? 10 02 00 00 ?? 89 4? }
*/

      $sys_x86      = { a0 00 00 00 24 02 00 00 40 00 00 00 [0-4] b8 00 00 00 6c 02 00 00 40 00 00 00 }
      $sys_x64      = { 88 01 00 00 3c 04 00 00 40 00 00 00 [0-4] e8 02 00 00 f8 02 00 00 40 00 00 00 }

   condition:
      (all of ($exe_x86_*)) or (all of ($exe_x64_*))
      // or (all of ($dll_*))
      or (any of ($sys_*))
}

rule wce
{
   meta:
      description      = "wce"
      author         = "Benjamin DELPY (gentilkiwi)"
      tool_author      = "Hernan Ochoa (hernano)"
      id = "857981ee-3f57-580b-8bfd-8d2109298e27"
   strings:
      $hex_legacy      = { 8b ff 55 8b ec 6a 00 ff 75 0c ff 75 08 e8 [0-3] 5d c2 08 00 }
      $hex_x86      = { 8d 45 f0 50 8d 45 f8 50 8d 45 e8 50 6a 00 8d 45 fc 50 [0-8] 50 72 69 6d 61 72 79 00 }
      $hex_x64      = { ff f3 48 83 ec 30 48 8b d9 48 8d 15 [0-16] 50 72 69 6d 61 72 79 00 }
   condition:
      any of them
}

rule power_pe_injection
{
   meta:
      description      = "PowerShell with PE Reflective Injection"
      author         = "Benjamin DELPY (gentilkiwi)"
      id = "a71fe9f2-9c2a-5650-a5c7-116b76f10db6"
   strings:
      $str_loadlib   = "0x53, 0x48, 0x89, 0xe3, 0x48, 0x83, 0xec, 0x20, 0x66, 0x83, 0xe4, 0xc0, 0x48, 0xb9"
   condition:
      $str_loadlib
}

rule Mimikatz_Logfile
{
   meta:
      description = "Detects a log file generated by malicious hack tool mimikatz"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      score = 80
      date = "2015/03/31"
      id = "921d85fc-fb4d-57ed-b4ac-203d5c6f1e8e"
   strings:
      $s1 = "SID               :" ascii fullword
      $s2 = "* NTLM     :" ascii fullword
      $s3 = "Authentication Id :" ascii fullword
      $s4 = "wdigest :" ascii fullword
   condition:
      all of them
}

rule Mimikatz_Strings {
   meta:
      description = "Detects Mimikatz strings"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "not set"
      date = "2016-06-08"
      score = 65
      id = "d8f63b71-c66c-5c10-9268-2d8970f7c8a1"
   strings:
      $x1 = "sekurlsa::logonpasswords" fullword wide ascii
      $x2 = "List tickets in MIT/Heimdall ccache" fullword ascii wide
      $x3 = "kuhl_m_kerberos_ptt_file ; LsaCallKerberosPackage %08x" fullword ascii wide
      $x4 = "* Injecting ticket :" fullword wide ascii
      $x5 = "mimidrv.sys" fullword wide ascii
      $x6 = "Lists LM & NTLM credentials" fullword wide ascii
      $x7 = "\\_ kerberos -" wide ascii
      $x8 = "* unknow   :" fullword wide ascii
      $x9 = "\\_ *Password replace ->" wide ascii
      $x10 = "KIWI_MSV1_0_PRIMARY_CREDENTIALS KO" ascii wide
      $x11 = "\\\\.\\mimidrv" wide ascii
      $x12 = "Switch to MINIDUMP :" fullword wide ascii
      $x13 = "[masterkey] with password: %s (%s user)" fullword wide
      $x14 = "Clear screen (doesn't work with redirections, like PsExec)" fullword wide
      $x15 = "** Session key is NULL! It means allowtgtsessionkey is not set to 1 **" fullword wide
      $x16 = "[masterkey] with DPAPI_SYSTEM (machine, then user): " fullword wide
   condition:
      (
         ( uint16(0) == 0x5a4d and 1 of ($x*) ) or
         ( 3 of them )
      )
      /* exclude false positives */
      and not pe.imphash() == "77eaeca738dd89410a432c6bd6459907"
}

rule AppInitHook {
   meta:
      description = "AppInitGlobalHooks-Mimikatz - Hide Mimikatz From Process Lists - file AppInitHook.dll"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://goo.gl/Z292v6"
      date = "2015-07-15"
      score = 70
      hash = "e7563e4f2a7e5f04a3486db4cefffba173349911a3c6abd7ae616d3bf08cfd45"
      id = "73713011-3083-5cdf-b59c-f4da67d2d2ab"
   strings:
      $s0 = "\\Release\\AppInitHook.pdb" ascii
      $s1 = "AppInitHook.dll" fullword ascii
      $s2 = "mimikatz.exe" fullword wide
      $s3 = "]X86Instruction->OperandSize >= Operand->Length" fullword wide
      $s4 = "mhook\\disasm-lib\\disasm.c" fullword wide
      $s5 = "mhook\\disasm-lib\\disasm_x86.c" fullword wide
      $s6 = "VoidFunc" fullword ascii
   condition:
      uint16(0) == 0x5a4d and filesize < 500KB and 4 of them
}

rule HKTL_Mimikatz_SkeletonKey_in_memory_Aug20_1 {
   meta:
      description = "Detects Mimikatz SkeletonKey in Memory"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://twitter.com/sbousseaden/status/1292143504131600384?s=12"
      date = "2020-08-09"
      id = "e7c1c512-e944-5d87-ac57-cdc9ab7cf660"
   strings:
      $x1 = { 60 ba 4f ca c7 44 24 34 dc 46 6c 7a c7 44 24 38 
              03 3c 17 81 c7 44 24 3c 94 c0 3d f6 }
   condition:
      1 of them
}

rule HKTL_mimikatz_memssp_hookfn {
   meta:
      description = "Detects Default Mimikatz memssp module in-memory"
      author = "SBousseaden"
      date = "2020-08-26"
      reference = "https://github.com/sbousseaden/YaraHunts/blob/master/mimikatz_memssp_hookfn.yara"
      score = 70
      id = "89940110-8a5e-5a28-bf64-3b568f8ef1f8"
   strings: 
      $xc1 = { 48 81 EC A8 00 00 00 C7 84 24 88 00 00 00 ?? ?? 
               ?? ?? C7 84 24 8C 00 00 00 ?? ?? ?? ?? C7 84 24 
               90 00 00 00 ?? ?? ?? 00 C7 84 24 80 00 00 00 61 
               00 00 00 C7 44 24 40 5B 00 25 00 C7 44 24 44 30 
               00 38 00 C7 44 24 48 78 00 3A 00 C7 44 24 4C 25 
               00 30 00 C7 44 24 50 38 00 78 00 C7 44 24 54 5D 
               00 20 00 C7 44 24 58 25 00 77 00 C7 44 24 5C 5A 
               00 5C 00 C7 44 24 60 25 00 77 00 C7 44 24 64 5A 
               00 09 00 C7 44 24 68 25 00 77 00 C7 44 24 6C 5A 
               00 0A 00 C7 44 24 70 00 00 00 00 48 8D 94 24 80 
               00 00 00 48 8D 8C 24 88 00 00 00 48 B8 A0 7D ?? 
               ?? ?? ?? 00 00 FF D0 } // memssp creds logging function
      // $xc2 = {6D 69 6D 69 C7 84 24 8C 00 00 00 6C 73 61 2E C7 84 24 90 00 00 00 6C 6F 67} -  mimilsa.log
   condition: 
      $xc1 // you can set condition to $xc1 and not $xc2 to detect non lazy memssp users 
}

rule HKTL_mimikatz_icon {
    meta:
        description = "Detects mimikatz icon in PE file"
        license = "Detection Rule License 1.1 https://github.com/SigmaHQ/Detection-Rule-License"
        author = "Arnim Rupp"
        reference = "https://blog.gentilkiwi.com/mimikatz"
        date = "2023-02-18"
        score = 60
        hash1 = "61c0810a23580cf492a6ba4f7654566108331e7a4134c968c2d6a05261b2d8a1"
        hash2 = "1c3f584164ef595a37837701739a11e17e46f9982fdcee020cf5e23bad1a0925"
        hash3 = "c6bb98b24206228a54493274ff9757ce7e0cbb4ab2968af978811cc4a98fde85"
        hash4 = "721d3476cdc655305902d682651fffbe72e54a97cd7e91f44d1a47606bae47ab"
        hash5 = "c0f3523151fa307248b2c64bdaac5f167b19be6fccff9eba92ac363f6d5d2595"
        id = "2a5ea476-a30d-5eac-b57a-3fb49386c046"
    strings:
        $ico = {79 e1 d7 ff 7e e5 db ff 7f e8 dc ff 85 eb dd ff ba ff f1 ff 66 a0 b6 ff 01 38 61 ff 22 50 75 c3}
    condition:
        uint16(0) == 0x5A4D and
        $ico and
        filesize < 10MB
}



// ── gen_suspicious_strings.yar ──

rule Ping_Command_in_EXE {
   meta:
      description = "Detects an suspicious ping command execution in an executable"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "Internal Research"
      date = "2016-11-03"
      score = 60
      id = "937ab622-fbcf-5a31-a3ff-af2584484140"
   strings:
      $x1 = "cmd /c ping 127.0.0.1 -n " ascii
   condition:
      uint16(0) == 0x5a4d and all of them
}

rule GoogleBot_UserAgent {
   meta:
      description = "Detects the GoogleBot UserAgent String in an Executable"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "Internal Research"
      date = "2017-01-27"
      score = 65
      id = "621532ac-fc0b-5118-84b0-eac110693320"
   strings:
      $x1 = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" fullword ascii

      $fp1 = "McAfee, Inc." wide
   condition:
      ( uint16(0) == 0x5a4d and filesize < 500KB and $x1 and not 1 of ($fp*) )
}

rule Gen_Net_LocalGroup_Administrators_Add_Command {
   meta:
      description = "Detects an executable that contains a command to add a user account to the local administrators group"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "Internal Research"
      date = "2017-07-08"
      id = "9f6095fc-6d9f-5814-b407-f320191fd912"
   strings:
      $x1 = /net localgroup administrators [a-zA-Z0-9]{1,16} \/add/ nocase ascii
   condition:
      ( uint16(0) == 0x5a4d and filesize < 400KB and 1 of them )
}

rule Suspicious_Script_Running_from_HTTP {
   meta:
      description = "Detects a suspicious "
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://www.hybrid-analysis.com/sample/a112274e109c5819d54aa8de89b0e707b243f4929a83e77439e3ff01ed218a35?environmentId=100"
      score = 50
      date = "2017-08-20"
      id = "9ba84e9c-a32b-5f66-8d50-75344599cafc"
   strings:
      $s1 = "cmd /C script:http://" ascii nocase
      $s2 = "cmd /C script:https://" ascii nocase
      $s3 = "cmd.exe /C script:http://" ascii nocase
      $s4 = "cmd.exe /C script:https://" ascii nocase
   condition:
      1 of them
}

rule ReconCommands_in_File : FILE {
   meta:
      description = "Detects various recon commands in a single file"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://twitter.com/haroonmeer/status/939099379834658817"
      date = "2017-12-11"
      score = 40
      id = "62d59913-5dbd-512c-98ea-044bbb9ac2da"
   strings:
      $ = "tasklist"
      $ = "net time"
      $ = "systeminfo"
      $ = "whoami"
      $ = "nbtstat"
      $ = "net start"
      $ = "qprocess"
      $ = "nslookup"
   condition:
      filesize < 5KB and 4 of them
}

rule VBS_dropper_script_Dec17_1 {
   meta:
      description = "Detects a supicious VBS script that drops an executable"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "Internal Research"
      date = "2018-01-01"
      score = 80
      id = "60f23d32-0737-501f-bf1c-1ca32af62efc"
   strings:
      $s1 = "TVpTAQEAAAAEAA" // 14 samples in goodware archive
      $s2 = "TVoAAAAAAAAAAA" // 26 samples in goodware archive
      $s3 = "TVqAAAEAAAAEAB" // 75 samples in goodware archive
      $s4 = "TVpQAAIAAAAEAA" // 168 samples in goodware archive
      $s5 = "TVqQAAMAAAAEAA" // 28,529 samples in goodware archive

      $a1 = "= CreateObject(\"Wscript.Shell\")" fullword ascii
   condition:
      filesize < 600KB and $a1 and 1 of ($s*)
}

rule SUSP_PDB_Strings_Keylogger_Backdoor : HIGHVOL {
   meta:
      description = "Detects PDB strings used in backdoors or keyloggers"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "Internal Research"
      date = "2018-03-23"
      score = 65
      id = "190daadb-0de6-5665-a241-95c374dbda47"
   strings:
      $ = "\\Release\\PrivilegeEscalation"
      $ = "\\Release\\KeyLogger"
      $ = "\\Debug\\PrivilegeEscalation"
      $ = "\\Debug\\KeyLogger"
      $ = "Backdoor\\KeyLogger_"
      $ = "\\ShellCode\\Debug\\"
      $ = "\\ShellCode\\Release\\"
      $ = "\\New Backdoor"
   condition:
      uint16(0) == 0x5a4d and filesize < 1000KB
      and 1 of them
}

rule SUSP_Microsoft_Copyright_String_Anomaly_2 {
   meta:
      description = "Detects Floxif Malware"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "Internal Research"
      date = "2018-05-11"
      score = 60
      hash1 = "de055a89de246e629a8694bde18af2b1605e4b9b493c7e4aef669dd67acf5085"
      id = "3257aff0-b923-5e56-b67c-fa676341a102"
   strings:
      $s1 = "Microsoft(C) Windows(C) Operating System" fullword wide
   condition:
      uint16(0) == 0x5a4d and filesize < 200KB and 1 of them
}

rule SUSP_LNK_File_AppData_Roaming {
   meta:
      description = "Detects a suspicious link file that references to AppData Roaming"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://www.fireeye.com/blog/threat-research/2018/05/deep-dive-into-rig-exploit-kit-delivering-grobios-trojan.html"
      date = "2018-05-16"
      score = 50
      id = "d905e58f-ae2e-5dc2-b206-d0435b023df0"
   strings:
      $s2 = "AppData" fullword wide
      $s3 = "Roaming" fullword wide
      /* .exe\x00C:\Users\ */
      $s4 = { 00 2E 00 65 00 78 00 65 00 2E 00 43 00 3A 00 5C
              00 55 00 73 00 65 00 72 00 73 00 5C }
   condition:
      uint16(0) == 0x004c and uint32(4) == 0x00021401 and (
         filesize < 1KB and
         all of them
      )
}

rule SUSP_LNK_File_PathTraversal {
   meta:
      description = "Detects a suspicious link file that references a file multiple folders lower than the link itself"
      license = "Detection Rule License 1.1 https://github.com/Neo23x0/signature-base/blob/master/LICENSE"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://www.fireeye.com/blog/threat-research/2018/05/deep-dive-into-rig-exploit-kit-delivering-grobios-trojan.html"
      date = "2018-05-16"
      score = 40
      id = "f4f6709f-9c4d-5f0c-9826-97444d282adc"
   strings:
      $s1 = "..\\..\\..\\..\\..\\"
   condition:
      uint16(0) == 0x004c and uint32(4) == 0x00021401 and (
         filesize < 1KB and
         all of them
      )
}

rule SUSP_Script_Obfuscation_Char_Concat {
   meta:
      description = "Detects strings found in sample from CN group repo leak in October 2018"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://twitter.com/JaromirHorejsi/status/1047084277920411648"
      date = "2018-10-04"
      hash1 = "b30cc10e915a23c7273f0838297e0d2c9f4fc0ac1f56100eef6479c9d036c12b"
      id = "6d3bfdfd-ef8f-5740-ac1f-5835c7ce0f43"
   strings:
      $s1 = "\"c\" & \"r\" & \"i\" & \"p\" & \"t\"" ascii
   condition:
      1 of them
}

rule SUSP_PowerShell_IEX_Download_Combo {
   meta:
      description = "Detects strings found in sample from CN group repo leak in October 2018"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://twitter.com/JaromirHorejsi/status/1047084277920411648"
      date = "2018-10-04"
      hash1 = "13297f64a5f4dd9b08922c18ab100d3a3e6fdeab82f60a4653ab975b8ce393d5"
      id = "1dfedcb0-345c-548c-85ac-3c1e78bfd9e2"
   strings:
      $x1 = "IEX ((new-object net.webclient).download" ascii nocase

      $fp1 = "chocolatey.org"
      $fp2 = "Remote Desktop in the Appveyor"
      $fp3 = "/appveyor/" ascii
   condition:
      $x1 and not 1 of ($fp*)
}

rule SUSP_Win32dll_String {
   meta:
      description = "Detects suspicious string in executables"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://medium.com/@Sebdraven/apt-sidewinder-changes-theirs-ttps-to-install-their-backdoor-f92604a2739"
      date = "2018-10-24"
      hash1 = "7bd7cec82ee98feed5872325c2f8fd9f0ea3a2f6cd0cd32bcbe27dbbfd0d7da1"
      id = "b1c78386-c23d-5138-942a-3da90e5802cc"
   strings:
      $s1 = "win32dll.dll" fullword ascii
   condition:
      filesize < 60KB and all of them
}

rule SUSP_Modified_SystemExeFileName_in_File {
   meta:
      description = "Detecst a variant of a system file name often used by attackers to cloak their activity"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://www.symantec.com/blogs/threat-intelligence/seedworm-espionage-group"
      date = "2018-12-11"
      score = 65
      hash1 = "5723f425e0c55c22c6b8bb74afb6b506943012c33b9ec1c928a71307a8c5889a"
      hash2 = "f1f11830b60e6530b680291509ddd9b5a1e5f425550444ec964a08f5f0c1a44e"
      id = "97d91e1b-49b8-504e-9e9c-6cfb7c2afe41"
   strings:
      $s1 = "svchosts.exe" fullword wide
   condition:
      uint16(0) == 0x5a4d and filesize < 200KB and 1 of them
}

rule SUSP_JAVA_Class_with_VBS_Content {
   meta:
      description = "Detects a JAVA class file with strings known from VBS files"
      author = "Florian Roth"
      reference = "https://www.menlosecurity.com/blog/a-jar-full-of-problems-for-financial-services-companies"
      date = "2019-01-03"
      modified = "2025-03-20"
      score = 70
      hash1 = "e0112efb63f2b2ac3706109a233963c19750b4df0058cc5b9d3fa1f1280071eb"
      id = "472cbeaf-28e7-51a2-b2e6-96c1d9d05b26"
   strings:
      $a1 = "java/lang/String" ascii

      $s1 = ".vbs" ascii
      $s2 = "createNewFile" fullword ascii
      $s3 = "wscript" fullword ascii nocase

      $fp1 = "com/smm/"
      $fp2 = "install"
   condition:
      ( uint16(0) == 0xfeca or uint16(0) == 0xfacf or uint32(0) == 0xbebafeca ) 
      and filesize < 100KB 
      and $a1 
      and all of ($s*)
      and not 1 of ($fp*)
}

rule SUSP_RAR_with_PDF_Script_Obfuscation {
   meta:
      description = "Detects RAR file with suspicious .pdf extension prefix to trick users"
      author = "Florian Roth (Nextron Systems)"
      reference = "Internal Research"
      date = "2019-04-06"
      hash1 = "b629b46b009a1c2306178e289ad0a3d9689d4b45c3d16804599f23c90c6bca5b"
      id = "a3d2f5e9-3052-551b-8b2c-abcdd1ac2e48"
   strings:
      $s1 = ".pdf.vbe" ascii
      $s2 = ".pdf.vbs" ascii
      $s3 = ".pdf.ps1" ascii
      $s4 = ".pdf.bat" ascii
      $s5 = ".pdf.exe" ascii
   condition:
      uint32(0) == 0x21726152 and 1 of them
}

rule SUSP_Netsh_PortProxy_Command {
   meta:
      description = "Detects a suspicious command line with netsh and the portproxy command"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://docs.microsoft.com/en-us/windows-server/networking/technologies/netsh/netsh-interface-portproxy"
      date = "2019-04-20"
      score = 65
      hash1 = "9b33a03e336d0d02750a75efa1b9b6b2ab78b00174582a9b2cb09cd828baea09"
      id = "cbbd2042-572c-5283-bd45-e745b36733ad"
   strings:
      $x1 = "netsh interface portproxy add v4tov4 listenport=" ascii
   condition:
      1 of them
}

rule SUSP_DropperBackdoor_Keywords {
   meta:
      description = "Detects suspicious keywords that indicate a backdoor"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://blog.talosintelligence.com/2019/04/dnspionage-brings-out-karkoff.html"
      date = "2019-04-24"
      hash1 = "cd4b9d0f2d1c0468750855f0ed352c1ed6d4f512d66e0e44ce308688235295b5"
      id = "2942ba6d-a533-5954-bfcf-417262e2fac2"
   strings:
      $x4 = "DropperBackdoor" fullword wide ascii
   condition:
      uint16(0) == 0x5a4d and filesize < 1000KB and 1 of them
}

rule SUSP_SFX_cmd {
   meta:
      description = "Detects suspicious SFX as used by Gamaredon group"
      author = "Florian Roth (Nextron Systems)"
      reference = "Internal Research"
      date = "2018-09-27"
      hash1 = "965129e5d0c439df97624347534bc24168935e7a71b9ff950c86faae3baec403"
      id = "87e75fe6-c2d7-5cb4-9432-7c37dbfe94b8"
   strings:
      $s1 = /RunProgram=\"hidcon:[a-zA-Z0-9]{1,16}.cmd/ fullword ascii
   condition:
      uint16(0) == 0x5a4d and filesize < 2000KB and 1 of them
}

rule SUSP_XMRIG_Reference {
   meta:
      description = "Detects an executable with a suspicious XMRIG crypto miner reference"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://twitter.com/itaitevet/status/1141677424045953024"
      date = "2019-06-20"
      score = 70
      id = "0a7324ce-90dc-5e6a-b22a-c29eccf324e9"
   strings:
      $x1 = "\\xmrig\\" ascii
   condition:
      uint16(0) == 0x5a4d and filesize < 2000KB and 1 of them
}

rule SUSP_Just_EICAR {
   meta:
      description = "Just an EICAR test file - this is boring but users asked for it"
      author = "Florian Roth (Nextron Systems)"
      reference = "http://2016.eicar.org/85-0-Download.html"
      date = "2019-03-24"
      score = 40
      hash1 = "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"
      id = "e5eedd77-36e2-56a0-be0c-2553043c225a"
   strings:
      $s1 = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*" fullword ascii
   condition:
      uint16(0) == 0x3558 and filesize < 70 and $s1 at 0
}

rule SUSP_PDB_Path_Keywords {
   meta:
      description = "Detects suspicious PDB paths"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://twitter.com/stvemillertime/status/1179832666285326337?s=20"
      date = "2019-10-04"
      id = "cbd9b331-58bb-5b29-88a2-5c19f12893a9"
   strings:
      $ = "Debug\\Shellcode" ascii
      $ = "Release\\Shellcode" ascii
      $ = "Debug\\ShellCode" ascii
      $ = "Release\\ShellCode" ascii
      $ = "Debug\\shellcode" ascii
      $ = "Release\\shellcode" ascii
      $ = "shellcode.pdb" nocase ascii
      $ = "\\ShellcodeLauncher" ascii
      $ = "\\ShellCodeLauncher" ascii
      $ = "Fucker.pdb" ascii
      $ = "\\AVFucker\\" ascii
      $ = "ratTest.pdb" ascii
      $ = "Debug\\CVE_" ascii
      $ = "Release\\CVE_" ascii
      $ = "Debug\\cve_" ascii
      $ = "Release\\cve_" ascii
   condition:
      uint16(0) == 0x5a4d and 1 of them
}

rule SUSP_Disable_ETW_Jun20_1 {
   meta:
      description = "Detects method to disable ETW in ENV vars before executing a program"
      author = "Florian Roth (Nextron Systems)"
      reference = "https://gist.github.com/Cyb3rWard0g/a4a115fd3ab518a0e593525a379adee3"
      date = "2020-06-06"
      id = "ea5dee09-959e-5ef2-8f84-5497bdef0a05"
   strings:
      $x1 = "set COMPlus_ETWEnabled=0" ascii wide fullword
      $x2 = "$env:COMPlus_ETWEnabled=0" ascii wide fullword

      $s1 = "Software\\Microsoft.NETFramework" ascii wide
      $sa1 = "/v ETWEnabled" ascii wide fullword 
      $sa2 = " /d 0" ascii wide
      $sb4 = "-Name ETWEnabled"
      $sb5 = " -Value 0 "
   condition:
      1 of ($x*) or 3 of them 
}

rule SUSP_PE_Discord_Attachment_Oct21_1 {
   meta:
      description = "Detects suspicious executable with reference to a Discord attachment (often used for malware hosting on a legitimate FQDN)"
      author = "Florian Roth (Nextron Systems)"
      reference = "Internal Research"
      date = "2021-10-12"
      score = 70
      id = "7c217350-4a35-505d-950d-1bc989c14bc2"
   strings:
      $x1 = "https://cdn.discordapp.com/attachments/" ascii wide
   condition:
      uint16(0) == 0x5a4d
      and filesize < 5000KB 
      and 1 of them
}

rule SUSP_Encoded_Discord_Attachment_Oct21_1 {
   meta:
      description = "Detects suspicious encoded URL to a Discord attachment (often used for malware hosting on a legitimate FQDN)"
      author = "Florian Roth (Nextron Systems)"
      reference = "Internal Research"
      date = "2021-10-12"
      score = 70
      id = "06c086f4-8b79-5506-9e3f-b5d099106157"
   strings:
      /* base64 encoded forms */
      $enc_b01 = "Y2RuLmRpc2NvcmRhcHAuY29tL2F0dGFjaG1lbnRz" ascii wide
      $enc_b02 = "Nkbi5kaXNjb3JkYXBwLmNvbS9hdHRhY2htZW50c" ascii wide
      $enc_b03 = "jZG4uZGlzY29yZGFwcC5jb20vYXR0YWNobWVudH" ascii wide
      $enc_b04 = "AGMAZABuAC4AZABpAHMAYwBvAHIAZABhAHAAcAAuAGMAbwBtAC8AYQB0AHQAYQBjAGgAbQBlAG4AdABz" ascii wide
      $enc_b05 = "BjAGQAbgAuAGQAaQBzAGMAbwByAGQAYQBwAHAALgBjAG8AbQAvAGEAdAB0AGEAYwBoAG0AZQBuAHQAc" ascii wide
      $enc_b06 = "AYwBkAG4ALgBkAGkAcwBjAG8AcgBkAGEAcABwAC4AYwBvAG0ALwBhAHQAdABhAGMAaABtAGUAbgB0AH" ascii wide

      /* hex encoded forms */
      $enc_h01 = "63646E2E646973636F72646170702E636F6D2F6174746163686D656E7473" ascii wide
      $enc_h02 = "63646e2e646973636f72646170702e636f6d2f6174746163686d656e7473" ascii wide

      /* reversed string */
      $enc_r01 = "stnemhcatta/moc.ppadrocsid.ndc" ascii wide
   condition:
      filesize < 5000KB and 1 of them
}


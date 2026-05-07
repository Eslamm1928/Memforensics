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

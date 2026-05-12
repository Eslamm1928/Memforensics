rule MemForensics_Lab1_Test {
    meta:
        description = "Guaranteed hit rule to test the Custom YARA pipeline"
        author = "Eslam Ebrahim"
        target = "MemoryDump_Lab1"
        
    strings:
        // 1. هندور على اسم برنامج الرسام اللي ظهر عندك في الـ malfind
        $paint = "mspaint.exe" wide ascii nocase
        
        // 2. هندور على صلاحية مشهورة جداً الهاكرز بيستخدموها عشان يحقنوا الكود
        $priv = "SeDebugPrivilege" wide ascii
        
        // 3. هندور على الـ Command Line لأنه أساسي في أي اختراق
        $cmd = "cmd.exe" wide ascii nocase

    condition:
        // لو لقى أي واحدة من التلاتة دول، هيطلعلك نتيجة فوراً
        any of them
}
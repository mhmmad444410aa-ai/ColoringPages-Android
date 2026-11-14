#!/usr/bin/env python3
from pathlib import Path
import re
root=Path("source/ColoringPages/app")
def edit(path, fn):
    s=path.read_text(encoding="utf-8")
    t=fn(s)
    if s==t: raise RuntimeError("Patch had no effect: "+str(path))
    path.write_text(t,encoding="utf-8")
def replace_once(s, a, b):
    assert s.count(a)==1, "Unexpected source structure around: "+a[:80]
    return s.replace(a,b)
def main_patch(s):
    s=replace_once(s,'''                LaunchedEffect(preferences.adsDecision) {
                    if (preferences.adsDecision == "approved") adsManager.enableAfterParentAcknowledgement()
                    else adsManager.disable()
                }''','''                // Contextual, non-personalised ads are always child-directed.
                LaunchedEffect(Unit) { adsManager.enableForChildDirectedRequests() }''')
    s=replace_once(s,'    var gatePurpose by rememberSaveable { mutableStateOf("settings") }\n','')
    s=replace_once(s,'    var advertisingNotice by rememberSaveable { mutableStateOf(false) }\n','')
    s=replace_once(s,'if(preferences.adsDecision=="approved" && adsManager.isEnabled())','if(adsManager.isEnabled())')
    s=replace_once(s,'{gatePurpose="settings";parentGate=true}','{parentGate=true}')
    s=replace_once(s,'"parents"->ParentScreen(vm,preferences,storageError,{back()},{advertisingNotice=true})','"parents"->ParentScreen(vm,preferences,storageError,{back()})')
    start=s.index('    if(preferences.adsDecision=="unset") {')
    end=s.index('    if(parentGate) ParentGate(',start)
    s=s[:start]+s[end:]
    s=replace_once(s,'''    if(parentGate) ParentGate({parentGate=false},{
        parentGate=false;parentAuthorized=true
        if(gatePurpose=="ads")advertisingNotice=true else screen="parents"
    })''','''    if(parentGate) ParentGate({parentGate=false},{
        parentGate=false;parentAuthorized=true;screen="parents"
    })''')
    start=s.index('    if(advertisingNotice && parentAuthorized) {')
    s=s[:start]+'}\n'
    assert all(k not in s for k in ('advertisingNotice','ad_parent_title','ad_continue_without','preferences.adsDecision'))
    return s
edit(root/'src/main/java/com/mhmmad/coloringpages/MainActivity.kt',main_patch)
def parent_patch(s):
    s=replace_once(s,', onReviewAdvertising: () -> Unit) {',') {')
    s=replace_once(s,'''                    HorizontalDivider(color=MaterialTheme.colorScheme.surfaceVariant)
                    ListItem(headlineContent={Text(stringResource(R.string.ads_title))},supportingContent={Text(stringResource(if(preferences.adsDecision=="approved")R.string.ads_status else R.string.ads_inactive))},leadingContent={Icon(Icons.Rounded.Info,null)},trailingContent={TextButton(onClick=onReviewAdvertising){Text(stringResource(R.string.ad_parent_review))}})''','')
    return s
edit(root/'src/main/java/com/mhmmad/coloringpages/feature/parents/ParentScreens.kt',parent_patch)
edit(root/'src/main/java/com/mhmmad/coloringpages/ads/ChildSafeAdsManager.kt',lambda s:
    replace_once(replace_once(s,'fun enableAfterParentAcknowledgement()','fun enableForChildDirectedRequests()'),
    '/** Never initialises an advertising SDK before parent acknowledgement. */',
    '/** Contextual, non-personalised, child-directed ad requests only. */'))
edit(root/'build.gradle.kts',lambda s:
    replace_once(replace_once(s,'versionCode = 3','versionCode = 4'),'versionName = "1.2.0"','versionName = "1.2.1"'))
privacy={
"values":"""Last updated: 14 November 2026

Colouring progress remains locally on the device. Drawing works offline; contextual advertisements require internet access. Huawei Petal Ads may show only child-directed, non-personalised adverts. The app flags child-directed and under-age requests, limits ad content to general audiences, and does not request precise location. The ad SDK may process limited device, network and advertising events under its privacy terms, but drawings and colouring progress are not shared with it.

Local preferences and artworks are stored privately; exported PNG files go only to the selected document provider. Backups are disabled. Parents may erase local progress in the protected Parents area. The app has no option to enable or disable adverts. Please consult the published privacy policy and the Huawei Petal Ads privacy statement. Contact the developer through the store listing.""",
"values-ar":"""آخر تحديث: ١٤ نوفمبر ٢٠٢٦

يبقى تقدم التلوين والرسومات على الجهاز. يعمل التلوين دون إنترنت؛ أما الإعلانات السياقية فتحتاج إلى اتصال. قد تعرض Huawei Petal Ads إعلانات غير مخصصة وموجّهة للأطفال فقط. نحدد طلبات الأطفال ومن هم دون سن الموافقة، ونقصر تصنيف الإعلانات على المناسب للجميع، ولا نطلب الموقع الدقيق. قد تعالج حزمة الإعلانات إشارات محدودة من الجهاز والشبكة وأحداث الإعلان وفق سياسة خصوصيتها، لكن لا تُشارك معها الرسومات أو تقدّم التلوين.

تُحفظ التفضيلات والرسومات محليًا؛ ولا تُصدّر الصور إلا إلى الجهة التي يختارها المستخدم. النسخ الاحتياطي معطّل. يستطيع الوالدان حذف التقدم من منطقة الوالدين المحمية. لا يوجد خيار لتشغيل الإعلانات أو إيقافها. راجع سياسة الخصوصية المنشورة وبيان Huawei Petal Ads، وتواصل مع المطور عبر صفحة المتجر.""",
"values-pt-rBR":"""Atualizado em 14 de novembro de 2026

O progresso e os desenhos ficam no dispositivo. A pintura funciona offline; anúncios contextuais exigem internet. Huawei Petal Ads pode exibir apenas anúncios não personalizados direcionados a crianças. As solicitações são marcadas como destinadas a crianças e menores de idade, com classificação de conteúdo geral e sem solicitação de localização precisa. O SDK pode processar sinais limitados do dispositivo, rede e eventos de publicidade conforme sua política; nenhum desenho ou progresso é compartilhado com o serviço.

As preferências e obras ficam armazenadas localmente. Os PNGs são exportados somente quando solicitado. Os backups estão desativados. Responsáveis podem apagar o progresso na área protegida. Não há opção para ativar ou desativar anúncios. Consulte nossa política de privacidade publicada e a política da Huawei Petal Ads. Contato pela página da loja."""
}
for lang,body in privacy.items():
    path=root/'src/main/res'/lang/'strings.xml'
    txt=path.read_text(encoding="utf-8")
    txt,n=re.subn(r'(<string name="privacy_body">).*?(</string>)',lambda m:m.group(1)+body+m.group(2),txt,count=1,flags=re.S)
    assert n==1
    path.write_text(txt,encoding="utf-8")
print("No ad modal or preference toggle; child-protection flags retained; version 1.2.1")

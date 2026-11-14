package com.mhmmad.coloringpages.ads

import android.util.Log
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.huawei.hms.ads.BannerAdSize
import com.huawei.hms.ads.banner.BannerView

/** Shown on gallery/home browsing pages only, never inside the colour canvas. */
@Composable
fun ChildSafeBanner(modifier: Modifier = Modifier) {
    val lifecycleOwner = LocalLifecycleOwner.current
    var banner by remember { mutableStateOf<BannerView?>(null) }
    DisposableEffect(lifecycleOwner, banner) {
        val view = banner
        val observer = LifecycleEventObserver { _, event ->
            try {
                when (event) {
                    Lifecycle.Event.ON_RESUME -> view?.resume()
                    Lifecycle.Event.ON_PAUSE -> view?.pause()
                    else -> Unit
                }
            } catch (_: Exception) { }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
            try { view?.destroy() } catch (_: Exception) { }
        }
    }
    AndroidView(
        factory = { context ->
            BannerView(context).also { view ->
                banner = view
                view.adId = AdPolicy.bannerId
                view.bannerAdSize = BannerAdSize.BANNER_SIZE_320_50
                try { view.loadAd(AdPolicy.request()) }
                catch (e: Exception) { Log.w("ColouringAds", "Banner not available", e) }
            }
        },
        modifier = modifier.fillMaxWidth().height(55.dp)
    )
}

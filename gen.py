import os

PKG = "com/example/comicfloat"
BASE = "comicfloat"

files = {}

files["settings.gradle.kts"] = r'''pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "comicfloat"
include(":app")
'''

files["build.gradle.kts"] = r'''plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.24" apply false
}
'''

files["gradle.properties"] = r'''org.gradle.jvmargs=-Xmx3g -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
'''

files["app/build.gradle.kts"] = r'''plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.comicfloat"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.comicfloat"
        minSdk = 30
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("com.google.mlkit:text-recognition:16.0.1")
    implementation("com.google.mlkit:translate:17.0.3")
}
'''

files["app/src/main/AndroidManifest.xml"] = r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:allowBackup="false"
        android:label="@string/app_name"
        android:theme="@android:style/Theme.DeviceDefault.Light.NoActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".FloatService"
            android:exported="true"
            android:label="@string/app_name"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/accessibility_config" />
        </service>
    </application>
</manifest>
'''

files["app/src/main/res/xml/accessibility_config.xml"] = r'''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeWindowStateChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault"
    android:canTakeScreenshot="true"
    android:description="@string/svc_desc"
    android:notificationTimeout="100" />
'''

files["app/src/main/res/values/strings.xml"] = r'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">แปลลอย</string>
    <string name="svc_desc">แสดงปุ่มลอยเพื่อจับภาพหน้าจอ อ่านข้อความอังกฤษ และวางคำแปลไทยทับบนหน้าจอ ทำงานในเครื่อง ไม่ส่งภาพออกไปที่ไหน</string>
</resources>
'''

files["app/src/main/java/" + PKG + "/MainActivity.kt"] = r'''package com.example.comicfloat

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val pad = (16 * resources.displayMetrics.density).toInt()

        val col = LinearLayout(this)
        col.orientation = LinearLayout.VERTICAL
        col.setPadding(pad, pad * 2, pad, pad)

        val title = TextView(this)
        title.text = "แปลลอย"
        title.textSize = 24f
        col.addView(title)

        val help = TextView(this)
        help.textSize = 16f
        help.setPadding(0, pad, 0, pad)
        help.text = "วิธีเปิดใช้งาน\n\n" +
            "1. กดปุ่มที่ 1 แล้วกดจุดสามจุดมุมขวาบน เลือก \"อนุญาตการตั้งค่าที่ถูกจำกัด\" (ถ้าไม่มีเมนูนี้ ข้ามไปข้อ 2)\n\n" +
            "2. กดปุ่มที่ 2 เลือก \"แปลลอย\" แล้วเปิดสวิตช์ และกดอนุญาต\n\n" +
            "3. จะมีปุ่มกลมสีส้มเขียนว่า \"แปล\" ลอยอยู่ ลากย้ายตำแหน่งได้\n\n" +
            "4. เปิดการ์ตูนใน Chrome แล้วแตะปุ่ม คำแปลไทยจะวางทับบนหน้าจอ แตะที่ใดก็ได้เพื่อปิดคำแปล แล้วเลื่อนอ่านต่อ\n\n" +
            "ครั้งแรกต้องต่อเน็ตเพื่อโหลดโมเดลแปลภาษา หลังจากนั้นใช้ออฟไลน์ได้ ภาพหน้าจอไม่ถูกบันทึกเป็นไฟล์"
        col.addView(help)

        val b1 = Button(this)
        b1.text = "1) ปลดล็อกการตั้งค่าที่ถูกจำกัด (หน้าข้อมูลแอพ)"
        b1.setOnClickListener {
            startActivity(
                Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + packageName))
            )
        }
        col.addView(b1)

        val b2 = Button(this)
        b2.text = "2) เปิดการตั้งค่าการช่วยเหลือพิเศษ"
        b2.setOnClickListener {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        }
        col.addView(b2)

        val sv = ScrollView(this)
        sv.addView(col)
        setContentView(sv)
    }
}
'''

files["app/src/main/java/" + PKG + "/FloatService.kt"] = r'''package com.example.comicfloat

import android.accessibilityservice.AccessibilityService
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.PixelFormat
import android.graphics.Rect
import android.graphics.drawable.GradientDrawable
import android.os.Handler
import android.os.Looper
import android.util.TypedValue
import android.view.Display
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.view.accessibility.AccessibilityEvent
import android.widget.FrameLayout
import android.widget.TextView
import android.widget.Toast
import com.google.mlkit.common.model.DownloadConditions
import com.google.mlkit.nl.translate.TranslateLanguage
import com.google.mlkit.nl.translate.Translation
import com.google.mlkit.nl.translate.Translator
import com.google.mlkit.nl.translate.TranslatorOptions
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions

class FloatService : AccessibilityService() {

    private lateinit var wm: WindowManager
    private val ui = Handler(Looper.getMainLooper())
    private var button: TextView? = null
    private var overlay: FrameLayout? = null
    private var translator: Translator? = null
    private var ready = false
    private var busy = false
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val letterRe = Regex("[A-Za-z]{2,}")

    override fun onServiceConnected() {
        super.onServiceConnected()
        wm = getSystemService(WINDOW_SERVICE) as WindowManager
        addButton()
        prepareTranslator()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {}

    override fun onInterrupt() {}

    override fun onDestroy() {
        super.onDestroy()
        hideOverlay()
        try { button?.let { wm.removeView(it) } } catch (e: Exception) {}
        button = null
        translator?.close()
        recognizer.close()
    }

    private fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()

    private fun toast(msg: String) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
    }

    private fun prepareTranslator() {
        if (translator == null) {
            val opts = TranslatorOptions.Builder()
                .setSourceLanguage(TranslateLanguage.ENGLISH)
                .setTargetLanguage(TranslateLanguage.THAI)
                .build()
            translator = Translation.getClient(opts)
        }
        translator!!.downloadModelIfNeeded(DownloadConditions.Builder().build())
            .addOnSuccessListener {
                ready = true
                toast("พร้อมแปลแล้ว")
            }
            .addOnFailureListener {
                ready = false
                toast("โหลดโมเดลแปลไม่สำเร็จ ต้องต่อเน็ตครั้งแรก")
            }
    }

    private fun addButton() {
        val tv = TextView(this)
        tv.text = "แปล"
        tv.setTextColor(Color.WHITE)
        tv.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f)
        tv.gravity = Gravity.CENTER
        val bg = GradientDrawable()
        bg.shape = GradientDrawable.OVAL
        bg.setColor(Color.parseColor("#E8573D"))
        tv.background = bg
        tv.alpha = 0.9f

        val size = dp(52)
        val p = WindowManager.LayoutParams(
            size, size,
            WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        p.gravity = Gravity.TOP or Gravity.START
        p.x = dp(8)
        p.y = dp(220)

        var startX = 0f
        var startY = 0f
        var origX = 0
        var origY = 0
        var moved = false
        tv.setOnTouchListener { _, e ->
            when (e.action) {
                MotionEvent.ACTION_DOWN -> {
                    startX = e.rawX
                    startY = e.rawY
                    origX = p.x
                    origY = p.y
                    moved = false
                    true
                }
                MotionEvent.ACTION_MOVE -> {
                    val dx = e.rawX - startX
                    val dy = e.rawY - startY
                    if (Math.abs(dx) > dp(8) || Math.abs(dy) > dp(8)) moved = true
                    if (moved) {
                        p.x = origX + dx.toInt()
                        p.y = origY + dy.toInt()
                        wm.updateViewLayout(tv, p)
                    }
                    true
                }
                MotionEvent.ACTION_UP -> {
                    if (!moved) onTap()
                    true
                }
                else -> false
            }
        }
        wm.addView(tv, p)
        button = tv
    }

    private fun onTap() {
        if (busy) return
        if (!ready) {
            toast("กำลังโหลดโมเดลแปล ต้องต่อเน็ตครั้งแรก")
            prepareTranslator()
            return
        }
        busy = true
        button?.visibility = View.INVISIBLE
        ui.postDelayed({ capture() }, 200)
    }

    private fun finish(msg: String?) {
        busy = false
        button?.text = "แปล"
        button?.visibility = View.VISIBLE
        if (msg != null) toast(msg)
    }

    private fun capture() {
        takeScreenshot(Display.DEFAULT_DISPLAY, mainExecutor, object : TakeScreenshotCallback {
            override fun onSuccess(result: ScreenshotResult) {
                var bmp: Bitmap? = null
                try {
                    val hw = Bitmap.wrapHardwareBuffer(result.hardwareBuffer, result.colorSpace)
                    bmp = hw?.copy(Bitmap.Config.ARGB_8888, false)
                    hw?.recycle()
                } catch (e: Exception) {
                    bmp = null
                }
                try { result.hardwareBuffer.close() } catch (e: Exception) {}
                if (bmp == null) {
                    finish("จับภาพหน้าจอไม่สำเร็จ")
                    return
                }
                runOcr(bmp)
            }

            override fun onFailure(errorCode: Int) {
                finish("จับภาพหน้าจอไม่สำเร็จ (รหัส " + errorCode + ") รอสักครู่แล้วลองใหม่")
            }
        })
    }

    // การ์ตูนมักเป็นตัวพิมพ์ใหญ่ทั้งหมด แปลงเป็นตัวพิมพ์ปกติก่อนแปลเพื่อให้ผลดีขึ้น
    private fun norm(s: String): String {
        var t = s.replace("-\n", "").replace("\n", " ").replace(Regex("\\s+"), " ").trim()
        val letters = t.filter { it in 'A'..'Z' || it in 'a'..'z' }
        if (letters.length > 3 && letters == letters.uppercase()) {
            t = t.lowercase()
            t = Regex("(^|[.!?]\\s+)([a-z])").replace(t) { m ->
                m.groupValues[1] + m.groupValues[2].uppercase()
            }
            t = t.replace(Regex("\\bi\\b"), "I")
        }
        return t
    }

    private fun runOcr(bmp: Bitmap) {
        button?.text = "…"
        button?.visibility = View.VISIBLE
        val w = bmp.width
        val h = bmp.height
        recognizer.process(InputImage.fromBitmap(bmp, 0))
            .addOnSuccessListener { text ->
                bmp.recycle()
                val items = ArrayList<Pair<Rect, String>>()
                for (b in text.textBlocks) {
                    val r = b.boundingBox ?: continue
                    val t = norm(b.text)
                    if (letterRe.containsMatchIn(t)) items.add(Pair(r, t))
                    if (items.size >= 40) break
                }
                if (items.isEmpty()) {
                    finish("ไม่พบข้อความภาษาอังกฤษบนหน้าจอ")
                } else {
                    translateAll(items, w, h)
                }
            }
            .addOnFailureListener {
                bmp.recycle()
                finish("อ่านข้อความไม่สำเร็จ")
            }
    }

    private fun translateAll(items: List<Pair<Rect, String>>, bw: Int, bh: Int) {
        val tr = translator
        if (tr == null) {
            finish("ตัวแปลยังไม่พร้อม")
            return
        }
        val out = ArrayList<Pair<Rect, String>>()
        fun next(i: Int) {
            if (i >= items.size) {
                showOverlay(out, bw, bh)
                return
            }
            tr.translate(items[i].second)
                .addOnSuccessListener { th ->
                    out.add(Pair(items[i].first, th))
                    next(i + 1)
                }
                .addOnFailureListener { next(i + 1) }
        }
        next(0)
    }

    private fun showOverlay(res: List<Pair<Rect, String>>, bw: Int, bh: Int) {
        if (res.isEmpty()) {
            finish("แปลไม่สำเร็จ")
            return
        }
        val bounds = wm.currentWindowMetrics.bounds
        val sx = bounds.width().toFloat() / bw
        val sy = bounds.height().toFloat() / bh

        val root = FrameLayout(this)
        root.setBackgroundColor(Color.parseColor("#11000000"))
        val pad = dp(4)
        for ((r, th) in res) {
            val left = Math.max(0, (r.left * sx).toInt() - pad)
            val top = Math.max(0, (r.top * sy).toInt() - pad)
            val w = (r.width() * sx).toInt() + pad * 2
            val h = (r.height() * sy).toInt() + pad * 2

            val tv = TextView(this)
            tv.text = th
            tv.setTextColor(Color.parseColor("#1F1B16"))
            tv.gravity = Gravity.CENTER
            val bg = GradientDrawable()
            bg.cornerRadius = dp(6).toFloat()
            bg.setColor(Color.parseColor("#F5FFFFFF"))
            tv.background = bg
            tv.setPadding(dp(3), dp(2), dp(3), dp(2))
            tv.setAutoSizeTextTypeUniformWithConfiguration(8, 22, 1, TypedValue.COMPLEX_UNIT_SP)

            val lp = FrameLayout.LayoutParams(w, h)
            lp.leftMargin = left
            lp.topMargin = top
            root.addView(tv, lp)
        }
        root.setOnClickListener { hideOverlay() }

        val p = WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or
                WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        )
        p.gravity = Gravity.TOP or Gravity.START
        p.layoutInDisplayCutoutMode =
            WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
        try {
            wm.addView(root, p)
            overlay = root
            busy = false
            button?.visibility = View.INVISIBLE
        } catch (e: Exception) {
            finish("แสดงคำแปลไม่สำเร็จ")
        }
    }

    private fun hideOverlay() {
        overlay?.let {
            try { wm.removeView(it) } catch (e: Exception) {}
        }
        overlay = null
        busy = false
        button?.text = "แปล"
        button?.visibility = View.VISIBLE
    }
}
'''

for rel, content in files.items():
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("generated", len(files), "files in", BASE)

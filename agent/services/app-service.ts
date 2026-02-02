/**
 * 应用信息服务
 * 提供 APK 信息获取等功能
 */

import "frida-java-bridge";
import Java from "frida-java-bridge";

/**
 * 应用服务
 */
export class AppService {
    /**
     * 获取 APK 基本信息
     */
    static getApkInfo(): any {
        try {
            let result: any = {};
            
            Java.perform(() => {
                const context = Java.use('android.app.ActivityThread')
                    .currentApplication()
                    .getApplicationContext();
                
                const pkgInfo = context.getPackageManager()
                    .getPackageInfo(context.getPackageName(), 0);
                
                const appInfo = pkgInfo.applicationInfo.value;
                
                // 应用名称
                let appName = "Unknown";
                try {
                    const labelRes = appInfo.labelRes.value;
                    appName = context.getResources().getString(labelRes);
                } catch {}
                
                // 包名
                const packageName = context.getPackageName();
                
                // 版本信息
                const versionName = pkgInfo.versionName.value;
                const versionCode = pkgInfo.versionCode.value;
                const targetSdkVersion = appInfo.targetSdkVersion.value;
                
                // 应用大小
                let appSize = 0;
                try {
                    appSize = Java.use("java.io.File")
                        .$new(appInfo.sourceDir.value)
                        .length();
                } catch {}
                
                // 路径信息
                const sourceDir = appInfo.sourceDir.value;
                const dataDir = appInfo.dataDir.value;
                const nativeLibraryDir = appInfo.nativeLibraryDir.value;
                
                // 时间信息
                const firstInstallTime = pkgInfo.firstInstallTime.value;
                const lastUpdateTime = pkgInfo.lastUpdateTime.value;
                
                // 标志位
                const flags = appInfo.flags.value;
                const isDebuggable = (flags & 2) !== 0;
                const isBackupable = (flags & 32768) !== 0;
                
                // UID
                const uid = appInfo.uid.value;
                
                // 签名信息
                let signatures: any = {};
                try {
                    const pis = context.getPackageManager()
                        .getPackageInfo(packageName, 0x00000040);
                    const hexDigest = pis.signatures.value[0].toByteArray();
                    
                    signatures = {
                        md5: AppService.hexDigest(hexDigest, "MD5"),
                        sha1: AppService.hexDigest(hexDigest, "SHA-1"),
                        sha256: AppService.hexDigest(hexDigest, "SHA-256")
                    };
                } catch {}
                
                // Unity build-id (如果有)
                let unityBuildId = "";
                try {
                    const metaAppInfo = context.getPackageManager()
                        .getApplicationInfo(packageName, 0x00000080);
                    const metaData = metaAppInfo.metaData.value;
                    if (metaData) {
                        unityBuildId = metaData.getString("unity.build-id") || "";
                    }
                } catch {}
                
                result = {
                    app_name: appName,
                    package_name: packageName,
                    version_name: versionName,
                    version_code: versionCode,
                    target_sdk_version: targetSdkVersion,
                    uid: uid,
                    app_size: appSize,
                    app_size_mb: (appSize / 1024 / 1024).toFixed(2),
                    source_dir: sourceDir,
                    data_dir: dataDir,
                    native_library_dir: nativeLibraryDir,
                    first_install_time: new Date(firstInstallTime).toISOString(),
                    last_update_time: new Date(lastUpdateTime).toISOString(),
                    is_debuggable: isDebuggable,
                    is_backupable: isBackupable,
                    signatures: signatures,
                    unity_build_id: unityBuildId
                };
            });
            
            return result;
        } catch (e) {
            return { error: `Failed to get APK info: ${e}` };
        }
    }

    /**
     * 计算签名哈希
     */
    private static hexDigest(paramArrayOfByte: any, algorithm: string): string {
        try {
            const hexDigits = "0123456789abcdef";
            const localMessageDigest = Java.use("java.security.MessageDigest").getInstance(algorithm);
            localMessageDigest.update(paramArrayOfByte);
            const arrayOfByte = localMessageDigest.digest();
            
            let result = "";
            const strLength = algorithm === "MD5" ? 16 : (algorithm === "SHA-1" ? 20 : 32);
            
            for (let i = 0; i < strLength; i++) {
                const k = arrayOfByte[i];
                result += hexDigits[(0xF & k >>> 4)];
                result += hexDigits[(k & 0xF)];
            }
            
            return result;
        } catch {
            return "";
        }
    }
}

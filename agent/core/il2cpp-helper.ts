import "frida-il2cpp-bridge"

/**
 * IL2CPP 缓存管理
 */
export class Il2CppCache {
    private static _assemblies: Il2Cpp.Assembly[] | null = null;
    private static _images: Il2Cpp.Image[] | null = null;
    private static _imagesNames: string[] | null = null;
    private static _classes: Il2Cpp.Class[] | null = null;
    private static _methods: Il2Cpp.Method[] | null = null;

    static get assemblies(): Il2Cpp.Assembly[] {
        if (!this._assemblies) {
            this._assemblies = Il2Cpp.domain.assemblies;
        }
        return this._assemblies;
    }

    static get images(): Il2Cpp.Image[] {
        if (!this._images) {
            this._images = this.assemblies.map((assembly) => assembly.image);
        }
        return this._images;
    }

    static get imagesNames(): string[] {
        if (!this._imagesNames) {
            this._imagesNames = this.assemblies.map((assembly) => 
                assembly.image.name.split(".dll")[0]
            );
        }
        return this._imagesNames;
    }

    static get classes(): Il2Cpp.Class[] {
        if (!this._classes) {
            this._classes = Il2Cpp.domain.assemblies
                .map((assembly) => assembly.image)
                .flatMap((image) => image.classes);
        }
        return this._classes;
    }

    static get methods(): Il2Cpp.Method[] {
        if (!this._methods) {
            this._methods = [];
            Il2Cpp.domain.assemblies.forEach((assembly) => {
                assembly.image.classes.forEach((klass) => {
                    this._methods = this._methods!.concat(klass.methods);
                });
            });
            this._methods.sort((a, b) => a.virtualAddress.compare(b.virtualAddress));
        }
        return this._methods;
    }

    static clearCache(): void {
        this._assemblies = null;
        this._images = null;
        this._imagesNames = null;
        this._classes = null;
        this._methods = null;
    }
}

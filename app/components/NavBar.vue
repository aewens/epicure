<template>
    <nav class="flex items-center justify-between flex-wrap bg-black p-6">
        <div class="flex items-center flex-shrink-0 text-white mr-6">
            <span class="font-semibold text-xl tracking-tight">
                epicure
            </span>
        </div>
        <div class="w-full block flex-grow lg:flex lg:items-center lg:w-auto">
            <div class="text-sm lg:flex-grow">
                <a href="/api" class="block mt-4 lg:inline-block lg:mt-0 text-white hover:text-red-500 mr-4">
                    API
                </a>
                <nuxt-link to="/dashboard" class="block mt-4 lg:inline-block lg:mt-0 text-white hover:text-red-500 mr-4">
                    Dashboard
                </nuxt-link>
                <nuxt-link to="/blog" class="block mt-4 lg:inline-block lg:mt-0 text-white hover:text-red-500 mr-4">
                    Blog
                </nuxt-link>
                <nuxt-link to="/about" class="block mt-4 lg:inline-block lg:mt-0 text-white hover:text-red-500 mr-4">
                    About
                </nuxt-link>
            </div>
            <div>
                <a href="#" class="inline-block text-sm px-4 py-2 leading-none border rounded text-white border-white hover:border-transparent hover:text-black hover:bg-white mt-4 lg:mt-0">
                    Button
                </a>
            </div>
        </div>
    </nav>
</template>

<script>
export default {
    name: "nav-bar"//,
    // data () {
    //     return {};
    // }
};
</script>

<style>
</style>

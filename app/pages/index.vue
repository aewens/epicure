<template>
    <div class="container mx-auto py-5 flex flex-col">
        <h1 class="text-6xl text-center">Epicure</h1>
        <div class="bg-gray-900 shadow-lg px-5 py-5 my-10 rounded"
            v-for="(entries, db) in dbs" :key="db">
            <h2 class="text-xl text-center underline capitalize mb-2">
                {{ db }}
            </h2>
            <form class="w-full bg-gray-700 p-5 rounded">
                <div class="md:flex md:items-center mb-6"
                    v-for="field in schemas[db]" :key="field.id">
                    <div class="md:w-1/3 text-right px-4">
                        <label>
                            {{ field.title }}
                        </label>
                    </div>
                    <div class="md:w-2/3">
                        <input type="text" class="bg-gray-900 text-gray-200 rounded w-full py-2 px-4 leading-tight border border-gray-800 focus:border-white">
                    </div>
                </div>
                <div class="md:flex md:justify-center">
                    <div class="md:w-1/3">
                        <button class="w-full shadow rounded text-white bg-blue-900 px-4 py-2 focus:shadow-outline">
                            Add
                        </button>
                    </div>
                </div>
            </form>
            <table class="table-fixed w-full">
                <thead>
                    <th v-for="field in schemas[db]" :key="field.id"
                        :class="['px-4', 'py-2', 'w-1/' + schemas[db].length]">
                        {{ field.title }}
                    </th>
                </thead>
                <tbody>
                    <tr v-for="entry in entries" :key="entry.id">
                        <td v-for="(value, key) in entry" :key="key"
                            :class="['px-4', 'py-2', 'border', 
                            'w-1/' + entry.length]">
                            {{ value }}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>


<script>
import { mapState } from "vuex";
//import NavBar from "~/components/NavBar";

export default {
    //components: {
    //    NavBar
    //},
    async fetch ({ $axios, store }) {
        const api_tables = await $axios.get("/api/db");
        const api_tables_code = api_tables.status.toString()[0] == "2";
        const api_tables_status = api_tables.data.status == "success";

        if (api_tables_code && api_tables_status) {
            const tables = api_tables.data.data;
            const promises = tables.map(async (table) => {
                const api_route = `/api/db/${table}`;
                const api_db = await $axios.get(api_route);
                const api_db_code = api_db.status.toString()[0] == "2";
                const api_db_status = api_db.data.status == "success";
                if (api_db_code && api_db_status) {
                    const { entries, schema } = api_db.data.data;
                    store.commit("ADD_DATABASE", [table, entries]);

                    const properties = Object.keys(schema.properties);
                    const schema_keys = properties.map((prop) => {
                        return schema.properties[prop];
                    });
                    store.commit("ADD_SCHEMA", [table, schema_keys]);
                }
            });
        }
    },
    computed: {
        ...mapState(["dbs", "schemas"])
    },
}
</script>

<style>
</style>

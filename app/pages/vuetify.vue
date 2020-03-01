<template>
    <v-app id="inspire">
        <v-navigation-drawer v-model="drawer" app clipped>
            <v-list dense>
                <v-list-item link>
                    <v-list-item-action>
                        <v-icon>mdi-view-dashboard</v-icon>
                    </v-list-item-action>
                    <v-list-item-content>
                        <v-list-item-title>Dashboard</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
                <v-list-item link>
                    <v-list-item-action>
                        <v-icon>mdi-settings</v-icon>
                    </v-list-item-action>
                    <v-list-item-content>
                        <v-list-item-title>Settings</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list>
        </v-navigation-drawer>

        <v-app-bar app clipped-left>
            <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
            <v-toolbar-title>Epicure</v-toolbar-title>
        </v-app-bar>

        <v-content>
            <v-container class="fill-height" fluid>
                <v-row>
                    <v-col class="pa-4 col-sm-12" v-for="(entries, db) in dbs" v-bind:key="entries.id">
                        <v-card>
                            <v-card-title>{{ db }}</v-card-title>
                            <v-data-table
                                :headers="schemas[db]"
                                :items="entries"
                                :items-per-page="5"
                                class="elevation-1"
                                :loading="schemas[db].length == 0"
                                loading-text="Loading... Please wait">
                            </v-data-table>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
        </v-content>

        <v-footer app>
            <span>&copy; 2020 Austin Ewens</span>
        </v-footer>
    </v-app>
</template>

<script>
/*

<div v-for="(entries, db) in dbs">
    <h2>{{ db }}</h2>
    <table class="table-fixed">
        <thead>
            <th class="w-1/8 px-4 py-2">ID</th>
            <th class="w-1/8 px-4 py-2">PID</th>
            <th class="w-3/4 px-4 py-2">Raw</th>
        </thead>
        <tbody>
            <tr v-for="entry in entries" :key="entry.id">
                <td class="w-1/8 px-4 py-2">{{ entry.id }}</td>
                <td class="w-1/8 px-4 py-2">{{ entry.parent_id }}</td>
                <td class="w-3/4 px-4 py-2">{{ entry.raw_data }}</td>
            </tr>
        </tbody>
    </table>
</div>

*/

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
                        return {text: prop, value: prop};
                    });
                    store.commit("ADD_SCHEMA", [table, schema_keys]);
                }
            });
        }
    },
    computed: {
        ...mapState(["dbs", "schemas", "drawer"])
    },
    created () {
      this.$vuetify.theme.dark = true;
    },
}
</script>

<style>
</style>

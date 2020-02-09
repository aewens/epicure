<template>
    <div>
        <table class="table-fixed">
            <thead>
                <th class="w-1/8 px-4 py-2">ID</th>
                <th class="w-1/8 px-4 py-2">PID</th>
                <th class="w-3/4 px-4 py-2">Raw</th>
            </thead>
            <tbody>
                <tr v-for="ditem in data" :key="ditem.id">
                    <td class="w-1/8 px-4 py-2">{{ ditem.id }}</td>
                    <td class="w-1/8 px-4 py-2">{{ ditem.parent_id }}</td>
                    <td class="w-3/4 px-4 py-2">{{ ditem.raw_data }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
export default {
    name: "epicure-databases",
    data () {
        return {
            "tags": [],
            "data": [],
            "notes": [],
            "tagmap": [],
        };
    }
};
</script>

<style>
</style>


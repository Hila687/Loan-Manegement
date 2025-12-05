<!-- src/components/LoanTable.vue -->
<template>
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-gray-100 text-gray-700">
        <tr>
          <th class="p-3 text-left">Borrower</th>
          <th class="p-3 text-left">Phone</th>
          <th class="p-3 text-left">Email</th>
          <th class="p-3 text-left">Trustee</th>
          <th class="p-3 text-left">Amount</th>
        </tr>
      </thead>

      <tbody class="divide-y">
        <tr v-for="n in 5" :key="n" class="hover:bg-gray-50">
          <td class="p-3">Example Borrower</td>
          <td class="p-3">050-0000000</td>
          <td class="p-3">test@test.com</td>
          <td class="p-3">Yossi Cohen</td>
          <td class="p-3">1,000 ₪</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
// No props yet – still static layout stage
</script>

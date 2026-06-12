# PLUGIN MADE BY @RRRLz FOR @ZThon
# 𝖹Ꭵᥣᴢᥲ️ᥣ

from . import zedub


@zedub.zed_cmd(pattern="لوف ?(.*)")
async def _(event):
    t = event.pattern_match.group(1)
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        await event.edit(f"""{t}{t}{t}{t}{t}{t}{t}{t}
{t}{t}{t}{t}{t}{t}{t}{t}
             {t}{t}{t}
             {t}{t}{t}
             {t}{t}{t}
             {t}{t}{t}
             {t}{t}{t}
             {t}{t}{t}
             {t}{t}{t}
             {t}{t}{t} 
             {t}{t}{t}
{t}{t}{t}{t}{t}{t}{t}{t}
{t}{t}{t}{t}{t}{t}{t}{t}\n


{t}{t}
{t}{t}
{t}{t}
{t}{t}
{t}{t}
{t}{t}
{t}{t}
{t}{t}
{t}{t}{t}{t}{t}{t}{t}{t}
{t}{t}{t}{t}{t}{t}{t}{t}\n
⁭
           {t}{t}{t}{t}{t}
      {t}{t}{t}{t}{t}{t}{t}
   {t}{t}                       {t}{t}
 {t}{t}                          {t}{t}
{t}{t}                            {t}{t}
{t}{t}                            {t}{t}
 {t}{t}                           {t}{t}
   {t}{t}                       {t}{t}
       {t}{t}{t}{t}{t}{t}{t}
            {t}{t}{t}{t}{t}\n
⁭
{t}{t}                              {t}{t}
  {t}{t}                          {t}{t}
    {t}{t}                      {t}{t}
      {t}{t}                  {t}{t}
         {t}{t}             {t}{t}
           {t}{t}         {t}{t}
             {t}{t}     {t}{t}
               {t}{t} {t}{t}
                  {t}{t}{t}
                       {t}\n
⁭
{t}{t}{t}{t}{t}{t}{t}{t}
{t}{t}{t}{t}{t}{t}{t}{t}
{t}{t}
{t}{t}
{t}{t}{t}{t}{t}{t}
{t}{t}{t}{t}{t}{t}
{t}{t}
{t}{t}
{t}{t}{t}{t}{t}{t}{t}{t}
{t}{t}{t}{t}{t}{t}{t}{t}\n

{t}{t}                         {t}{t}
  {t}{t}                    {t}{t}
     {t}{t}              {t}{t}
        {t}{t}        {t}{t}
           {t}{t}  {t}{t}
              {t}{t}{t}
                {t}{t}
                {t}{t}
                {t}{t}
                {t}{t}
                {t}{t}\n
⁭
        {t}{t}{t}{t}{t}{t}
     {t}{t}{t}{t}{t}{t}{t}
   {t}{t}                     {t}{t}
 {t}{t}                         {t}{t}
{t}{t}                           {t}{t}
{t}{t}                           {t}{t}
 {t}{t}                         {t}{t}
   {t}{t}                     {t}{t}
      {t}{t}{t}{t}{t}{t}{t}
            {t}{t}{t}{t}{t}\n
⁭
{t}{t}                      {t}{t}
{t}{t}                      {t}{t}
{t}{t}                      {t}{t}
{t}{t}                      {t}{t}
{t}{t}                      {t}{t}
{t}{t}                      {t}{t}
{t}{t}                      {t}{t}
  {t}{t}                  {t}{t}
      {t}{t}{t}{t}{t}{t}
            {t}{t}{t}{t}""")
